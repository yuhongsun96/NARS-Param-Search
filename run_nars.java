import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;
import java.lang.reflect.*;

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
    public static void main(String args[]) throws Exception{
        //NARS using all defaults (last 2 represent narsese input file and number of cycles), see Shell.java in opennars repo
        String[] defaults = new String[] { "null", "null", "null", "null"};
        Nar nar = Shell.createNar(defaults);

        //Get parameters from args passed in when process created from python script
	nar.narParameters.PROJECTION_DECAY=0.1f;
	Class nar_class = nar.narParameters.getClass();
	Field[] nar_params = nar_class.getDeclaredFields();
        for(int i = 0; i < nar_params.length; i++) {
            System.out.println("Field = " + nar_params[i].toString());
         }
	
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
