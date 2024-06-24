import subprocess
import multiprocessing

from shell import main


def run_java():
    subprocess.run(["java", 
                    "-cp", 
                    "solver-common/target/solver-common-0.1.jar", 
                    "com.solver.Main"])


if __name__ == "__main__":
    java_process = multiprocessing.Process(target=run_java)
    java_process.start()
    main()
