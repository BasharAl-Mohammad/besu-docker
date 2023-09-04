import subprocess

BLOCK_PERIOD=[1,2,3,4,5]
DIFFICULTY=[1,2,3,4,5]
NB_NODES=[11,21,31,41,51,61,71,81,91,101]
# SEND_RATES=[500,1000,1500,2000,2500,3000]
SEND_RATES=[1000]


if __name__ == '__main__':
    
    for bps in BLOCK_PERIOD:
        for nn in NB_NODES:
            for rate in SEND_RATES:
                command = f"python3 run-report.py QBFT {nn} {bps} 30000 4 {rate}"
                subprocess.run(command,shell=True)

    for bps in BLOCK_PERIOD:
        for nn in NB_NODES:
            for rate in SEND_RATES:
                command = f"python3 run-report.py IBFT {nn} {bps} 30000 4 {rate}"
                subprocess.run(command,shell=True)


    for bps in BLOCK_PERIOD:
        for nn in NB_NODES:
            for rate in SEND_RATES:
                command = f"python3 run-report.py CLIQUE {nn} {bps} 30000 {rate}"
                subprocess.run(command,shell=True)


    for fd in DIFFICULTY:
        for nn in NB_NODES:
            for rate in SEND_RATES:
                command = f"python3 run-report.py ETHASH {nn} {fd} {rate}"
                subprocess.run(command,shell=True)
                
