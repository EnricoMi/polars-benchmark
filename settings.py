from pathlib import Path, PurePath
from typing import Optional, Literal, TypeAlias

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

IoType: TypeAlias = Literal["skip", "parquet", "feather", "csv"]


# Set via PATH_<NAME>
class Paths(BaseSettings):
    answers: Path = Path("data/answers")
    # use Path.from_uri with Python >= 3.13
    tables: Path = Path("s3://polars-cloud-0196fdda-9e66-7832-8f8f-6e5690fc41a7/data/tables")

    timings: Path = Path("output/run")
    timings_filename: str = "timings-cs2.csv"

    plots: Path = Path("output/plot")

    model_config = SettingsConfigDict(
        env_prefix="path_", env_file=".env", extra="ignore"
    )


# Set via RUN_<NAME>
class Run(BaseSettings):
    io_type: IoType = "parquet"

    iterations: int = 3
    log_timings: bool = True
    show_results: bool = False
    check_results: bool = False  # Only available for SCALE_FACTOR=1

    polars_show_plan: bool = False
    polars_eager: bool = False
    polars_old_streaming: bool = False
    polars_streaming: bool = False
    polars_cloud: bool = True
    polars_gpu: bool = False  # Use GPU engine?
    polars_gpu_device: int = 0  # The GPU device to run on for polars GPU
    # Which style of GPU memory resource to use
    # cuda -> cudaMalloc
    # cuda-pool -> Pool suballocator wrapped around cudaMalloc
    # managed -> cudaMallocManaged
    # managed-pool -> Pool suballocator wrapped around cudaMallocManaged
    # cuda-async -> cudaMallocAsync (comes with pool)
    # See https://docs.rapids.ai/api/rmm/stable/ for details on RMM memory resources
    use_rmm_mr: Literal[
        "cuda", "cuda-pool", "managed", "managed-pool", "cuda-async"
    ] = "cuda-async"

    polars_cloud_cpus: Optional[int] = None
    polars_cloud_memory: Optional[int] = None
    # https://aws.amazon.com/de/ec2/instance-types/c7a/
    # c7a.medium:   1 vCPUs / 2 GB memory
    # c7a.large:    2 vCPUs / 4 GB memory
    # c7a.xlarge:   4 vCPUs / 8 GB memory
    # c7a.2xlarge:  8 vCPUs / 16 GB memory
    # c7a.4xlarge:  16 vCPUs / 32 GB memory
    # c7a.8xlarge:  32 vCPUs / 64 GB memory
    # c7a.16xlarge: 64 vCPUs / 128 GB memory
    # c7a.24xlarge: 96 vCPUs / 192 GB memory
    polars_cloud_instance_type: Optional[str] = "c7a.8xlarge"  # use instance_type instead of cpus and memory, e.g. "t2.micro"
    polars_cloud_cluster_size: int = 2
    polars_cloud_workspace: Optional[str] = None

    modin_memory: int = 8_000_000_000  # Tune as needed for optimal performance

    spark_driver_memory: str = "32g"  # Tune as needed for optimal performance
    spark_executor_memory: str = "1g"  # Tune as needed for optimal performance
    spark_log_level: str = "ERROR"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def include_io(self) -> bool:
        return self.io_type != "skip"

    model_config = SettingsConfigDict(
        env_prefix="run_", env_file=".env", extra="ignore"
    )


class Plot(BaseSettings):
    show: bool = False
    n_queries: int = 7
    y_limit: float | None = None

    model_config = SettingsConfigDict(
        env_prefix="plot_", env_file=".env", extra="ignore"
    )


class Settings(BaseSettings):
    scale_factor: float = 100.0
    num_partitions: Optional[int] = 100

    paths: Paths = Paths()
    plot: Plot = Plot()
    run: Run = Run()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dataset_base_dir(self) -> Path:
        return self.paths.tables / f"scale-{self.scale_factor}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
