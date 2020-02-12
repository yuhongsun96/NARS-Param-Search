import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

import org.opennars.main.Nar;
import org.opennars.storage.Memory;
import org.opennars.entity.BudgetValue;
import org.opennars.entity.Concept;
import org.opennars.entity.Task;
import org.opennars.operator.Operation;
import org.opennars.operator.Operator;
import org.opennars.language.Term;
import org.opennars.interfaces.Timable;
import org.opennars.main.Shell;
import org.opennars.main.Debug;

class run_nars{

    private static void set_nars_params(Nar nar, String args[]){
        for(int i = 1; i < args.length; i += 2){
            if(args[i].equals("-NOVELTY_HORIZON")){nar.narParameters.NOVELTY_HORIZON=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-DECISION_THRESHOLD")){nar.narParameters.DECISION_THRESHOLD=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-CONCEPT_BAG_SIZE")){nar.narParameters.CONCEPT_BAG_SIZE=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-CONCEPT_BAG_LEVELS")){nar.narParameters.CONCEPT_BAG_LEVELS=Integer.parseInt(args[i+1]);}
            

            else if(args[i].equals("-DURATION")){nar.narParameters.DURATION=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-HORIZON")){nar.narParameters.HORIZON=Integer.parseInt(args[i+1]);}
            
            
            else if(args[i].equals("-TRUTH_EPSILON")){nar.narParameters.TRUTH_EPSILON=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-BUDGET_EPSILON")){nar.narParameters.BUDGET_EPSILON=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-BUDGET_THRESHOLD")){nar.narParameters.BUDGET_THRESHOLD=Float.parseFloat(args[i+1]);}


            else if(args[i].equals("-DEFAULT_CONFIRMATION_EXPECTATION")){nar.narParameters.DEFAULT_CONFIRMATION_EXPECTATION=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-ALWAYS_CREATE_CONCEPT")){
                if(args[i+1].equals("1")){nar.narParameters.ALWAYS_CREATE_CONCEPT=true;}
                else{nar.narParameters.ALWAYS_CREATE_CONCEPT=false;}
            }
            else if(args[i].equals("-DEFAULT_CREATION_EXPECTATION")){nar.narParameters.DEFAULT_CREATION_EXPECTATION=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_CREATION_EXPECTATION_GOAL")){nar.narParameters.DEFAULT_CREATION_EXPECTATION_GOAL=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-DEFAULT_JUDGMENT_CONFIDENCE")){nar.narParameters.DEFAULT_JUDGMENT_CONFIDENCE=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_JUDGMENT_PRIORITY")){nar.narParameters.DEFAULT_JUDGMENT_PRIORITY=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_JUDGMENT_DURABILITY")){nar.narParameters.DEFAULT_JUDGMENT_DURABILITY=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-DEFAULT_QUESTION_PRIORITY")){nar.narParameters.DEFAULT_QUESTION_PRIORITY=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_QUESTION_DURABILITY")){nar.narParameters.DEFAULT_QUESTION_DURABILITY=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-DEFAULT_GOAL_CONFIDENCE")){nar.narParameters.DEFAULT_GOAL_CONFIDENCE=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_GOAL_PRIORITY")){nar.narParameters.DEFAULT_GOAL_PRIORITY=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_GOAL_DURABILITY")){nar.narParameters.DEFAULT_GOAL_DURABILITY=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_QUEST_PRIORITY")){nar.narParameters.DEFAULT_QUEST_PRIORITY=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_QUEST_DURABILITY")){nar.narParameters.DEFAULT_QUEST_DURABILITY=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-BAG_THRESHOLD")){nar.narParameters.BAG_THRESHOLD=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-FORGET_QUALITY_RELATIVE")){nar.narParameters.FORGET_QUALITY_RELATIVE=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-REVISION_MAX_OCCURRENCE_DISTANCE")){nar.narParameters.REVISION_MAX_OCCURRENCE_DISTANCE=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-TASK_LINK_BAG_SIZE")){nar.narParameters.TASK_LINK_BAG_SIZE=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-TASK_LINK_BAG_LEVELS")){nar.narParameters.TASK_LINK_BAG_LEVELS=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-TERM_LINK_BAG_SIZE")){nar.narParameters.TERM_LINK_BAG_SIZE=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-TERM_LINK_BAG_LEVELS")){nar.narParameters.TERM_LINK_BAG_LEVELS=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-TERM_LINK_MAX_MATCHED")){nar.narParameters.TERM_LINK_MAX_MATCHED=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-NOVEL_TASK_BAG_SIZE")){nar.narParameters.NOVEL_TASK_BAG_SIZE=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-NOVEL_TASK_BAG_LEVELS")){nar.narParameters.NOVEL_TASK_BAG_LEVELS=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-NOVEL_TASK_BAG_SELECTIONS")){nar.narParameters.NOVEL_TASK_BAG_SELECTIONS=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-SEQUENCE_BAG_SIZE")){nar.narParameters.SEQUENCE_BAG_SIZE=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-SEQUENCE_BAG_LEVELS")){nar.narParameters.SEQUENCE_BAG_LEVELS=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-OPERATION_BAG_SIZE")){nar.narParameters.OPERATION_BAG_SIZE=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-OPERATION_BAG_LEVELS")){nar.narParameters.OPERATION_BAG_LEVELS=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-OPERATION_SAMPLES")){nar.narParameters.OPERATION_SAMPLES=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-PROJECTION_DECAY")){nar.narParameters.PROJECTION_DECAY=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-MAXIMUM_EVIDENTAL_BASE_LENGTH")){nar.narParameters.MAXIMUM_EVIDENTAL_BASE_LENGTH=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-TERMLINK_MAX_REASONED")){nar.narParameters.TERMLINK_MAX_REASONED=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-TERM_LINK_RECORD_LENGTH")){nar.narParameters.TERM_LINK_RECORD_LENGTH=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-CONCEPT_BELIEFS_MAX")){nar.narParameters.CONCEPT_BELIEFS_MAX=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-CONCEPT_QUESTIONS_MAX")){nar.narParameters.CONCEPT_QUESTIONS_MAX=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-CONCEPT_GOALS_MAX")){nar.narParameters.CONCEPT_GOALS_MAX=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-reliance")){nar.narParameters.reliance=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DISCOUNT_RATE")){nar.narParameters.DISCOUNT_RATE=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-IMMEDIATE_ETERNALIZATION")){
                if(args[i+1].equals("1")){nar.narParameters.IMMEDIATE_ETERNALIZATION=true;}
                else{nar.narParameters.IMMEDIATE_ETERNALIZATION=false;}
            }
            else if(args[i].equals("-SEQUENCE_BAG_ATTEMPTS")){nar.narParameters.SEQUENCE_BAG_ATTEMPTS=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-CONDITION_BAG_ATTEMPTS")){nar.narParameters.CONDITION_BAG_ATTEMPTS=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-DERIVATION_PRIORITY_LEAK")){nar.narParameters.DERIVATION_PRIORITY_LEAK=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DERIVATION_DURABILITY_LEAK")){nar.narParameters.DERIVATION_DURABILITY_LEAK=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-CURIOSITY_DESIRE_CONFIDENCE_MUL")){nar.narParameters.CURIOSITY_DESIRE_CONFIDENCE_MUL=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-CURIOSITY_DESIRE_PRIORITY_MUL")){nar.narParameters.CURIOSITY_DESIRE_PRIORITY_MUL=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-CURIOSITY_DESIRE_DURABILITY_MUL")){nar.narParameters.CURIOSITY_DESIRE_DURABILITY_MUL=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-CURIOSITY_FOR_OPERATOR_ONLY")){
                if(args[i+1].equals("1")){nar.narParameters.CURIOSITY_FOR_OPERATOR_ONLY=true;}
                else{nar.narParameters.CURIOSITY_FOR_OPERATOR_ONLY=false;}
            }

            else if(args[i].equals("-BREAK_NAL_HOL_BOUNDARY")){
                if(args[i+1].equals("1")){nar.narParameters.BREAK_NAL_HOL_BOUNDARY=true;}
                else{nar.narParameters.BREAK_NAL_HOL_BOUNDARY=false;}
            }

            else if(args[i].equals("-QUESTION_GENERATION_ON_DECISION_MAKING")){
                if(args[i+1].equals("1")){nar.narParameters.QUESTION_GENERATION_ON_DECISION_MAKING=true;}
                else{nar.narParameters.QUESTION_GENERATION_ON_DECISION_MAKING=false;}
            }
            else if(args[i].equals("-HOW_QUESTION_GENERATION_ON_DECISION_MAKING")){
                if(args[i+1].equals("1")){nar.narParameters.HOW_QUESTION_GENERATION_ON_DECISION_MAKING=true;}
                else{nar.narParameters.HOW_QUESTION_GENERATION_ON_DECISION_MAKING=false;}
            }

            else if(args[i].equals("-ANTICIPATION_CONFIDENCE")){nar.narParameters.ANTICIPATION_CONFIDENCE=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-ANTICIPATION_TOLERANCE")){nar.narParameters.ANTICIPATION_TOLERANCE=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-RETROSPECTIVE_ANTICIPATIONS")){
                if(args[i+1].equals("1")){nar.narParameters.RETROSPECTIVE_ANTICIPATIONS=true;}
                else{nar.narParameters.RETROSPECTIVE_ANTICIPATIONS=false;}
            }

            else if(args[i].equals("-SATISFACTION_TRESHOLD")){nar.narParameters.SATISFACTION_TRESHOLD=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-COMPLEXITY_UNIT")){nar.narParameters.COMPLEXITY_UNIT=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-INTERVAL_ADAPT_SPEED")){nar.narParameters.INTERVAL_ADAPT_SPEED=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-TASKLINK_PER_CONTENT")){nar.narParameters.TASKLINK_PER_CONTENT=Integer.parseInt(args[i+1]);}

            else if(args[i].equals("-DEFAULT_FEEDBACK_PRIORITY")){nar.narParameters.DEFAULT_FEEDBACK_PRIORITY=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DEFAULT_FEEDBACK_DURABILITY")){nar.narParameters.DEFAULT_FEEDBACK_DURABILITY=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-CONCEPT_FORGET_DURATIONS")){nar.narParameters.CONCEPT_FORGET_DURATIONS=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-TERMLINK_FORGET_DURATIONS")){nar.narParameters.TERMLINK_FORGET_DURATIONS=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-TASKLINK_FORGET_DURATIONS")){nar.narParameters.TASKLINK_FORGET_DURATIONS=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-EVENT_FORGET_DURATIONS")){nar.narParameters.EVENT_FORGET_DURATIONS=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-VARIABLE_INTRODUCTION_COMBINATIONS_MAX")){nar.narParameters.VARIABLE_INTRODUCTION_COMBINATIONS_MAX=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-VARIABLE_INTRODUCTION_CONFIDENCE_MUL")){nar.narParameters.VARIABLE_INTRODUCTION_CONFIDENCE_MUL=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-ANTICIPATIONS_PER_CONCEPT_MAX")){nar.narParameters.ANTICIPATIONS_PER_CONCEPT_MAX=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-MOTOR_BABBLING_CONFIDENCE_THRESHOLD")){nar.narParameters.MOTOR_BABBLING_CONFIDENCE_THRESHOLD=Float.parseFloat(args[i+1]);}

            else if(args[i].equals("-THREADS_AMOUNT")){nar.narParameters.THREADS_AMOUNT=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-VOLUME")){nar.narParameters.VOLUME=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-MILLISECONDS_PER_STEP")){nar.narParameters.MILLISECONDS_PER_STEP=Integer.parseInt(args[i+1]);}
            else if(args[i].equals("-STEPS_CLOCK")){
                if(args[i+1].equals("1")){nar.narParameters.STEPS_CLOCK=true;}
                else{nar.narParameters.STEPS_CLOCK=false;}
            }

            else if(args[i].equals("-DERIVATION_DURABILITY_LEAK")){nar.narParameters.DERIVATION_DURABILITY_LEAK=Float.parseFloat(args[i+1]);}
            else if(args[i].equals("-DERIVATION_PRIORITY_LEAK")){nar.narParameters.DERIVATION_PRIORITY_LEAK=Float.parseFloat(args[i+1]);}
        }
    }

    //Run NARS in shell to use pipes
    public static void main(String args[]) throws Exception{
        //NARS using all defaults (last 2 represent narsese input file and number of cycles), see Shell.java in opennars repo
        String[] defaults = new String[] { "null", "null", "null", "null"};
        Nar nar = Shell.createNar(defaults);

        //Get parameters from args passed in when process created from python script
        set_nars_params(nar, args);
        
        //Required for objective function chain_length
        Debug.PARENTS = true;
        
        //Start NARS in shell
        new Shell(nar).run(defaults);

        //Randomize initial state since NARS is pseudo-random
        TimeUnit.SECONDS.sleep(1);
        
        //Pass in toothbrush.nal file
        String toothbrushfile = new String(Files.readAllBytes(Paths.get(args[0])));
        nar.addInput(toothbrushfile);
    } 
}
