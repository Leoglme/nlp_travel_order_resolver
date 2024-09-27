import torch
import time
import psutil  # Pour obtenir les informations sur le CPU
import GPUtil  # Pour obtenir les informations sur le GPU

class DeviceManager:
    def __init__(self):
        # Initialisation avec la vérification de la disponibilité du GPU
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            gpu_info = torch.cuda.get_device_properties(0)
            print(f"GPU disponible : {torch.cuda.get_device_name(0)} avec {gpu_info.total_memory / 1e9:.2f} GB de mémoire")
        else:
            self.device = torch.device("cpu")
            print("GPU non disponible, utilisation du CPU")

    def use_cpu(self):
        """
        Passe sur le CPU.
        """
        self.device = torch.device("cpu")
        print("Passage sur le CPU.")

    def use_gpu(self):
        """
        Passe sur le GPU, s'il est disponible.
        """
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            print(f"Passage sur le GPU : {torch.cuda.get_device_name(0)}")
        else:
            print("Aucun GPU disponible, utilisation du CPU.")
            self.device = torch.device("cpu")

    def print_cpu_info(self):
        """
        Affiche les informations du CPU (nombre de cœurs, fréquence).
        """
        cpu_freq = psutil.cpu_freq().current
        cpu_cores = psutil.cpu_count(logical=False)
        print(f"CPU : {cpu_cores} cœurs à {cpu_freq:.2f} MHz")

    def print_gpu_info(self):
        """
        Affiche les informations du GPU (nom, mémoire).
        """
        if torch.cuda.is_available():
            gpu = GPUtil.getGPUs()[0]
            print(f"GPU : {gpu.name} avec {gpu.memoryTotal:.2f} GB de mémoire")

    def compare_devices(self):
        """
        Compare les performances du CPU et du GPU en entraînant un modèle simple et en mesurant le temps.
        Affiche également les informations sur la puissance du GPU et du CPU.
        """
        # Afficher les infos CPU et GPU
        self.print_cpu_info()
        self.print_gpu_info()

        # Simple modèle pour tester la performance (réseau de neurones simple)
        model = torch.nn.Linear(1000, 1000)

        # Génération d'une matrice aléatoire de taille raisonnable pour le test
        input_data = torch.randn(1000, 1000)

        # Fonction pour mesurer le temps d'exécution sur un device donné
        def measure_performance(device, name):
            model.to(device)
            input_data_device = input_data.to(device)

            start_time = time.time()
            iterations = 1000
            for _ in range(iterations):
                output = model(input_data_device)
            end_time = time.time()

            elapsed_time = end_time - start_time
            iters_per_second = iterations / elapsed_time
            print(f"Temps d'exécution sur {name} : {elapsed_time:.4f} secondes ({iters_per_second:.2f} itérations/seconde)")
            return elapsed_time, iters_per_second

        # Mesurer les performances sur CPU
        cpu_time, cpu_iters_per_sec = measure_performance(torch.device("cpu"), "CPU")

        # Mesurer les performances sur GPU si disponible
        if torch.cuda.is_available():
            gpu_time, gpu_iters_per_sec = measure_performance(torch.device("cuda"), "GPU")
        else:
            gpu_time = float('inf')
            gpu_iters_per_sec = 0

        # Comparaison et conclusion
        if gpu_time < cpu_time:
            print(f"Le GPU ({torch.cuda.get_device_name(0)}) est plus rapide.")
            print(f"GPU : {gpu_iters_per_sec:.2f} itérations/seconde")
            return "gpu"
        else:
            print("Le CPU est plus rapide.")
            print(f"CPU : {cpu_iters_per_sec:.2f} itérations/seconde")
            return "cpu"