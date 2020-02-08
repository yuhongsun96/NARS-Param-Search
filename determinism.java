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
        int num_runs = 10;

	// Target statements of toothbrush.nal
        String target1 = "(^lighter,{SELF},toothbrush)! %1.00;0.39%"; 
        String target2 = "(^reshape,{SELF},toothbrush)! %1.00;0.26%";

	int hits = 0;
        for(int i = 0; i < num_runs; i++){
            System.out.println("Iteration: " + Integer.toString(i));

            // Initialize NARS
            final Nar nar = new Nar();
	    
	    // Set Hyperparameters
	    nar.narParameters.DERIVATION_PRIORITY_LEAK = 0.1f; //0.4f default
            nar.narParameters.VARIABLE_INTRODUCTION_COMBINATIONS_MAX = 8; //8 default
            nar.narParameters.SEQUENCE_BAG_ATTEMPTS = 10; //10 default
            nar.narParameters.TERM_LINK_MAX_MATCHED = 50; //10 default

            // Pass in toothbrush.nal file
            String toothbrushfile = new String(Files.readAllBytes(Paths.get("toothbrush.nal")));
            nar.addInput(toothbrushfile);

            // Capture NARS output
            ByteArrayOutputStream nar_stream = new ByteArrayOutputStream();
            new TextOutputHandler(nar, new PrintStream(nar_stream), 0.0f);

            // Run NARS for 300,000 Cycles
            nar.cycles(100000);

            String nar_out = nar_stream.toString();

            // Check if target statements were generated
	    if(nar_out.contains(target1)){
		System.out.println("Statement 1 found");
	    }
	    if(nar_out.contains(target2)){
		System.out.println("Statement 2 found");
            }
	    if(nar_out.contains(target1) && nar_out.contains(target2)){
		hits += 1;
	    }
        }
	System.out.println(Integer.toString(num_runs) + " runs were conducted");
	System.out.println("NARS deduced the target statement: " + Integer.toString(hits) + " times");
    } 
}
