import subprocess
process = subprocess.call(['java', '-cp', '.:opennars-3.0.4-SNAPSHOT.jar', 'run_nars', '0.7', '8', '10', '10'], stdout=subprocess.PIPE, shell=True)
#process = subprocess.call(['java', '-jar', 'opennars-3.0.4-SNAPSHOT.jar'])
#stdout = process.communicate()[0]
#output = process.stdout.readline()
#print(output)
print('reached')

