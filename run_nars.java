import java.nio.file.Files;
import java.nio.file.Paths;

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
    //Run NARS in shell to use pipes
    public static void main(String args[]) throws Exception{
        //NARS using all defaults (no specified id, config file, etc), see Shell.java in opennars repo
        String[] defaults = new String[] { "null", "null", "null", "null"};
        Nar nar = Shell.createNar(defaults);

        //Get parameters from args passed in when process created from python script
        nar.narParameters.DERIVATION_PRIORITY_LEAK=Float.parseFloat(args[0]); //0.4f default
        nar.narParameters.VARIABLE_INTRODUCTION_COMBINATIONS_MAX=Integer.parseInt(args[1]); //8 default
        nar.narParameters.SEQUENCE_BAG_ATTEMPTS=Integer.parseInt(args[2]); //10 default
        nar.narParameters.TERM_LINK_MAX_MATCHED=Integer.parseInt(args[3]); //10 default

        Debug.PARENTS = true;
        
        //Start NARS in shell
        new Shell(nar).run(defaults);
        
        //Pass in toothbrush.nal file
        String toothbrushfile = new String ( Files.readAllBytes( Paths.get("toothbrush.nal") ) );
        nar.addInput(toothbrushfile);
    } 
}
