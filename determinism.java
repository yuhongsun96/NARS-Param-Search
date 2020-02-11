import java.nio.file.Files;
import java.nio.file.Paths;

import org.opennars.main.Nar;
import org.opennars.io.events.EventHandler;
import org.opennars.io.events.OutputHandler.OUT;
import java.io.PrintStream;
import org.opennars.io.events.TextOutputHandler;
import java.io.ByteArrayOutputStream;

class determinism{
    public static void main(String args[]) throws Exception{
    int num_runs = 100;
    int nars_cycle_cap = 10000;

    // Target statements of toothbrush.nal
    String target1 = "(^lighter,{SELF},toothbrush)!"; 
    String target2 = "(^reshape,{SELF},toothbrush)!";

	int hits = 0;
    for(int i = 0; i < num_runs; i++){
        System.out.println("\n\nIteration: " + Integer.toString(i));

        // Initialize NARS
        final Nar nar = new Nar();
    
        // Set Hyperparameters
        nar.narParameters.DERIVATION_PRIORITY_LEAK = 0.2f; // 0.4f default
        nar.narParameters.VARIABLE_INTRODUCTION_COMBINATIONS_MAX = 8; // 8 default
        nar.narParameters.SEQUENCE_BAG_ATTEMPTS = 10; // 10 default
        nar.narParameters.TERM_LINK_MAX_MATCHED = 15; // 10 default

        // Pass in toothbrush.nal file
        String toothbrushfile = new String(Files.readAllBytes(Paths.get("toothbrush.nal")));
        nar.addInput(toothbrushfile);

        // Capture NARS output
        ByteArrayOutputStream nar_stream = new ByteArrayOutputStream();
        new TextOutputHandler(nar, new PrintStream(nar_stream), 0.0f);

        // Run NARS for some set number of Cycles
        nar.cycles(nars_cycle_cap);

        String[] nar_out = nar_stream.toString().split("\n");

        // Check if target statements were generated
        boolean found1, found2, updated;
        found1 = found2 = updated = false;
        for(String line : nar_out){
            if(line.contains(target1) && !found1){
                System.out.println("\nStatement 1 found: " + line);
                found1 = true;
            }
            if(line.contains(target2) && !found2){
                System.out.println("\nStatement 2 found: " + line);
                found2 = true;
            }
            if(found1 && found2 && !updated){
                hits += 1;
                updated = true;
            }
        }
    }
	System.out.println("\n\n" + Integer.toString(num_runs) + " runs were conducted");
	System.out.println("NARS deduced the target statement: " + Integer.toString(hits) + " times");
    } 
}
