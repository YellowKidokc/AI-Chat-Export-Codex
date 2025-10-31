from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .config import AppConfig
from .pipeline import IngestionPipeline

app = typer.Typer(add_completion=False)
console = Console()


def _resolve_paths(inputs: list[str]) -> list[Path]:
    return [Path(item).expanduser().resolve() for item in inputs]


@app.command()
def run(
    inputs: list[str] = typer.Argument(..., help="Paths to chat export files or archives."),
    workdir: str = typer.Option(".aicec/workdir", help="Temporary working directory."),
    output: str = typer.Option(".aicec/markdown", help="Directory for generated Markdown files."),
    manifest: Optional[str] = typer.Option(None, help="Path to write the manifest JSON."),
) -> None:
    workdir_path = Path(workdir).expanduser().resolve()
    output_path = Path(output).expanduser().resolve()
    manifest_path = Path(manifest).expanduser().resolve() if manifest else None

    config = AppConfig(
        input_paths=_resolve_paths(inputs),
        workdir=workdir_path,
        output_dir=output_path,
        manifest_path=manifest_path,
    )
    pipeline = IngestionPipeline(config)
    manifest_path = pipeline.run()
    console.print(f"Pipeline finished. Manifest available at {manifest_path}")


@app.command()
def preview(
    inputs: list[str] = typer.Argument(..., help="Paths to chat export files or archives."),
    workdir: str = typer.Option(".aicec/workdir", help="Temporary working directory."),
    limit: int = typer.Option(5, help="Number of conversations to preview."),
) -> None:
    workdir_path = Path(workdir).expanduser().resolve()
    config = AppConfig(
        input_paths=_resolve_paths(inputs),
        workdir=workdir_path,
        output_dir=workdir_path / "preview",
    )
    pipeline = IngestionPipeline(config)
    previews = pipeline.preview(limit=limit)
    for item in previews:
        console.print(f"- {item}")


if __name__ == "__main__":  # pragma: no cover
    app()
