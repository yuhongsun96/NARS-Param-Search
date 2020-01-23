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
import org.opennars.gui.NARSwing;
import org.opennars.main.Shell;

class run_nars{
    public static void main(String args[]) throws Exception{
        String[] defaults = new String[] { "null", "null", "null", "null"};
        Nar nar = Shell.createNar(defaults);
        nar.narParameters.DERIVATION_PRIORITY_LEAK=Float.parseFloat(args[0]); //0.4f default
        nar.narParameters.VARIABLE_INTRODUCTION_COMBINATIONS_MAX=Integer.parseInt(args[1]); //8 default
        nar.narParameters.SEQUENCE_BAG_ATTEMPTS=Integer.parseInt(args[2]); //10 default
        nar.narParameters.TERM_LINK_MAX_MATCHED=Integer.parseInt(args[3]); //10 default
        //new NARSwing(nar);
        //nar.start();
        
        new Shell(nar).run(defaults);
        
        String toothbrushfile = new String ( Files.readAllBytes( Paths.get("toothbrush.nal") ) );

        nar.addInput(toothbrushfile);
    } 
}
