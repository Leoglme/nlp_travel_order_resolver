import torch
import time
import psutil  # To get CPU information
import GPUtil  # To get GPU information

"""
Class to manage the device (CPU/GPU) used for training and inference.
"""


class DeviceManager:
    def __init__(self):
        # Initializing with GPU availability check
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            gpu_info = torch.cuda.get_device_properties(0)
            print(
                f"GPU available : {torch.cuda.get_device_name(0)} with {gpu_info.total_memory / 1e9:.2f} GB of memory")
        else:
            self.device = torch.device("cpu")
            print("GPU not available, CPU usage")

    def use_cpu(self):
        self.device = torch.device("cpu")
        print("Passage sur le CPU.")

    def use_gpu(self):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            print(f"Switching to the GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("No GPU available, CPU usage.")
            self.device = torch.device("cpu")

    """
    Compares CPU and GPU performance by training a simple model and measuring time.
    """
    def use_best_device(self):
        best_device = self.compare_devices()
        print(f"The fastest device is: {best_device}")

        if best_device == "gpu":
            self.use_gpu()
        else:
            self.use_cpu()

    """
    Shows CPU information (number of cores, frequency).
    """

    def print_cpu_info(self):
        cpu_freq = psutil.cpu_freq().current
        cpu_cores = psutil.cpu_count(logical=False)
        print(f"CPU : {cpu_cores} cœurs à {cpu_freq:.2f} MHz")

    """
    Shows GPU information (name, memory).
    """

    def print_gpu_info(self):
        if torch.cuda.is_available():
            gpu = GPUtil.getGPUs()[0]
            print(f"GPU : {gpu.name} with {gpu.memoryTotal:.2f} GB of memory")

    """
    Compares CPU and GPU performance by training a simple model and measuring time.
    Also displays GPU and CPU power information.
    """

    def compare_devices(self):
        # Show CPU and GPU info
        self.print_cpu_info()
        self.print_gpu_info()

        # Simple model to test performance (simple neural network)
        model = torch.nn.Linear(1000, 1000)

        # Generating a random matrix of reasonable size for testing
        input_data = torch.randn(1000, 1000)

        # Function to measure execution time on a given device
        def measure_performance(device, name):
            model.to(device)
            input_data_device = input_data.to(device)

            start_time = time.time()
            iterations = 1000
            for _ in range(iterations):
                model(input_data_device)
            end_time = time.time()

            elapsed_time = end_time - start_time
            iters_per_second = iterations / elapsed_time
            print(f"Execution time on {name} : {elapsed_time:.4f} seconds ({iters_per_second:.2f} iterations/second)")
            return elapsed_time, iters_per_second

        # Measuring CPU performance
        cpu_time, cpu_iters_per_sec = measure_performance(torch.device("cpu"), "CPU")

        # Measure performance on GPU if available
        if torch.cuda.is_available():
            gpu_time, gpu_iters_per_sec = measure_performance(torch.device("cuda"), "GPU")
        else:
            gpu_time = float('inf')
            gpu_iters_per_sec = 0

        # Comparison and conclusion
        if gpu_time < cpu_time:
            print(f"The GPU ({torch.cuda.get_device_name(0)}) is faster.")
            print(f"GPU : {gpu_iters_per_sec:.2f} iterations/second")
            return "gpu"
        else:
            print("The CPU is faster.")
            print(f"CPU : {cpu_iters_per_sec:.2f} iterations/second")
            return "cpu"
