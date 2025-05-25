import time
from datetime import datetime
import os

def monitor_logs():
    log_file = "connection_manager.log"
    
    print("🔍 Monitorando logs em tempo real...")
    print("Pressione Ctrl+C para sair\n")
    
    try:
        with open(log_file, "r") as f:
            # Move para o final do arquivo
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                    
                # Imprime a linha com formatação colorida
                if "ERROR" in line:
                    print(f"\033[91m{line}\033[0m", end="")  # Vermelho
                elif "WARNING" in line:
                    print(f"\033[93m{line}\033[0m", end="")  # Amarelo
                elif "INFO" in line:
                    print(f"\033[92m{line}\033[0m", end="")  # Verde
                else:
                    print(line, end="")
                    
    except KeyboardInterrupt:
        print("\n\n✋ Monitoramento encerrado")
    except Exception as e:
        print(f"\n❌ Erro ao monitorar logs: {e}")

if __name__ == "__main__":
    monitor_logs() 