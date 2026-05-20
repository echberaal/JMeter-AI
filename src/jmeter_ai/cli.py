"""CLI entrypoint for the JMeter AI Assistant."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import click


@click.group()
def main() -> None:
    """JMeter AI Assistant — AI-powered JMeter scripting."""


@main.command()
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the input document.",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(path_type=Path),
    help="Path for the output JSON file.",
)
def extract(file: Path, output: Path) -> None:
    """Extract a test scenario from a document (Stage 1)."""
    try:
        scenario = asyncio.run(_run_extraction(file))
    except KeyboardInterrupt:
        click.echo("\nAborted.", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    # Serialize
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(scenario.model_dump(mode="json"), default=str),
        encoding="utf-8",
    )

    # Summary
    meta = scenario.extraction_metadata
    total_steps = sum(len(t.steps) for t in scenario.transactions)
    click.echo(f"\n\u2705 Extraction complete: {scenario.name}")
    click.echo(f"   Transactions: {len(scenario.transactions)}")
    click.echo(f"   Steps:        {total_steps}")
    click.echo(f"   Variables:    {len(scenario.global_variables)}")
    if meta:
        click.echo(f"   Confidence:   {meta.overall_confidence:.1%}")
        if meta.warnings:
            click.echo(f"   Warnings:     {len(meta.warnings)}")
            for w in meta.warnings:
                click.echo(f"     ⚠ {w}")
    click.echo(f"   Output:       {output}")


async def _run_extraction(file: Path) -> Any:
    """Run the Stage 1 pipeline."""
    from jmeter_ai.stages.stage1_ingestion import Stage1Pipeline

    pipeline = Stage1Pipeline()
    return await pipeline.run(file)


if __name__ == "__main__":
    main()
