import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;
import java.lang.reflect.*;
import java.util.Random;

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

/**
 * A wrapper class for NARS
 * Sets internal parameters using command line arguments
 * Runs NARS such that outputs are displayed to the shell
 */
class run_nars{
    /**
     * Runs NARS with all defaults in Shell mode
     * Updates NARS parameters with user specified
     * 
     * @param args  The first argument is the Narsese file to pass to NARS
     *              All following arguments should be parameter/value pairs
     *              following format: -PARAM_NAME param_value (int, float, boolean)
     */
    public static void main(String args[]) throws Exception{
        //NARS using all defaults (last 2 represent narsese input file and number of cycles), see Shell.java in opennars repo
        String[] defaults = new String[] { "null", "null", "null", "null"};
        Nar nar = Shell.createNar(defaults);

        //Read the Narsese file contents
        String toothbrushfile = new String(Files.readAllBytes(Paths.get(args[0])));
        
        //Get parameters from args passed in when process created from python script
        Field[] nar_params = nar.narParameters.getClass().getDeclaredFields();
        for(int argNum = 1; argNum < args.length; argNum += 2){
            String passedField = args[argNum].substring(1);
            String passedValue = args[argNum + 1];
            //Use reflection to get fields matching the string
            for(int fieldNum = 0; fieldNum < nar_params.length; fieldNum++){
                Field narsField = nar_params[fieldNum];
                //If the field name matches nar.narParameters, check against the 3 types of params
                if(passedField.equals(narsField.getName())){
                    if(narsField.getType() == int.class){
                        narsField.setInt(nar.narParameters, Integer.parseInt(passedValue));
                    }
                    if(narsField.getType() == float.class){
                        narsField.setFloat(nar.narParameters, Float.parseFloat(passedValue));
                    }
                    if(narsField.getType() == boolean.class){
                        if(passedValue.equals("0")){narsField.setBoolean(nar.narParameters, false);}
                        else{narsField.setBoolean(nar.narParameters, true);}
                    }
                }
            }
        }
        
        //Required for objective function chain_length
        Debug.PARENTS = true;
        
        //Start NARS in shell
        new Shell(nar).run(defaults);

        //Randomly choose an initial state since NARS is pseudo-random
        Random r = new Random();
        TimeUnit.MILLISECONDS.sleep(r.nextInt(100));
        
        //Give NARS input string, output should begin coming on the shell
        nar.addInput(toothbrushfile);
    } 
}
