import subprocess

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {e.cmd}")
        print(e.output.decode('utf-8'))
        exit(1)

# Command 1
command1 = 'npx caliper bind --caliper-bind-sut besu:latest'
run_command(command1)

# Command 2
command2 = 'npx caliper launch manager \
    --caliper-workspace . \
    --caliper-benchconfig benchmarks/scenario/simple/config.yaml \
    --caliper-networkconfig config.json --caliper-flow-skip-install'
run_command(command2)
