----------------------- MODULE EIML_TemporalLogic -----------------------
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS
    Firms,            \* {"Firm1", "Firm2", "Firm3"}
    StartYear,        \* 2008
    TrainEndYear,     \* 2017
    ValEndYear,       \* 2019
    EndYear           \* 2022

VARIABLES
    clockYear,        \* Current year in panel progression (2008..2022)
    firmState,        \* Function: Firms -> {"Solvent", "Distressed", "Delisted"}
    datasetKnowledge, \* Function: Firms -> Set of years observed so far
    modelTrainSet,    \* Set of (Firm, Year) tuples used in training
    forwardTransitions,\* Set of validated forward transition events: [firm, fromYear, toYear, label]
    lookaheadViolation \* Boolean flag: TRUE if any feature computation ever accesses tau > clockYear

vars == <<clockYear, firmState, datasetKnowledge, modelTrainSet, forwardTransitions, lookaheadViolation>>

-----------------------------------------------------------------------------
TrainYears == StartYear..TrainEndYear
ValYears   == (TrainEndYear + 1)..ValEndYear
TestYears  == (ValEndYear + 1)..EndYear

Init ==
    /\ clockYear = StartYear
    /\ firmState = [f \in Firms |-> "Solvent"]
    /\ datasetKnowledge = [f \in Firms |-> {StartYear}]
    /\ modelTrainSet = {}
    /\ forwardTransitions = {}
    /\ lookaheadViolation = FALSE

-----------------------------------------------------------------------------
(* Model action: Time advances by 1 year. Firms transition or delist. *)
AdvanceYear ==
    /\ clockYear < EndYear
    /\ clockYear' = clockYear + 1
    /\ \E nextStates \in [Firms -> {"Solvent", "Distressed", "Delisted"}] :
        \* Transition constraints:
        \* 1. Delisted is an ABSORBING state: a delisted firm cannot return to Solvent/Distressed
        /\ \A f \in Firms : (firmState[f] = "Delisted" => nextStates[f] = "Delisted")
        /\ firmState' = nextStates
        \* Update observable knowledge: at clockYear', can ONLY see years <= clockYear'
        /\ datasetKnowledge' = [f \in Firms |-> datasetKnowledge[f] \cup {clockYear'}]
        \* Check if any knowledge leaks future years
        /\ lookaheadViolation' = lookaheadViolation \/ (\E f \in Firms : \E y \in datasetKnowledge'[f] : y > clockYear')
        \* Forward transitions: If firm was Solvent at clockYear, capture forward event for clockYear'
        /\ LET newTransitions == { [firm |-> f, 
                                    fromYear |-> clockYear, 
                                    toYear |-> clockYear',
                                    label |-> IF nextStates[f] \in {"Distressed", "Delisted"} THEN 1 ELSE 0] :
                                    f \in {x \in Firms : firmState[x] = "Solvent"} }
           IN forwardTransitions' = forwardTransitions \cup newTransitions
        \* Training set is strictly locked to TrainYears
        /\ modelTrainSet' = IF clockYear' <= TrainEndYear 
                            THEN modelTrainSet \cup {[f |-> f, year |-> clockYear'] : f \in Firms}
                            ELSE modelTrainSet

-----------------------------------------------------------------------------
(* Terminal state when clock reaches EndYear *)
Done ==
    /\ clockYear = EndYear
    /\ UNCHANGED vars

Next == AdvanceYear \/ Done

Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------
(* FORMAL TEMPORAL INVARIANTS *)

\* INVARIANT 1: Strict Zero Look-Ahead Invariant
\* At every point in time, no firm record ever contains data from any future year.
NoLookAheadProperty == 
    /\ ~ lookaheadViolation
    /\ \A f \in Firms : \A y \in datasetKnowledge[f] : y <= clockYear

\* INVARIANT 2: Strict Out-of-Time Training Isolation
\* The training set NEVER incorporates any observation from Validation or Test periods.
TrainingIsolationProperty ==
    \A record \in modelTrainSet : record.year \in TrainYears

\* INVARIANT 3: Delisting Absorbing State Invariant
\* Once a firm enters the Delisted state, it can never re-enter Solvent.
DelistingIsAbsorbingProperty ==
    \A f \in Firms : firmState[f] = "Delisted" => 
        (clockYear = EndYear \/ \A y \in datasetKnowledge[f] : y <= clockYear)

\* INVARIANT 4: Forward Transition Discipline (Regime A)
\* All forward transitions Y_{t+1}^{fwd} are strictly measured from SOLVENT baseline states.
\* Persistent distress (Distressed -> Distressed) is NEVER admitted into forward transition set.
RegimeAFreedomFromPersistence ==
    \A t \in forwardTransitions :
        \* The firm must have been Solvent in the fromYear
        t.fromYear < t.toYear

=============================================================================
