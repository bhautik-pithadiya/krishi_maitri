from pathlib import Path

def render_prompt(name: str, **vars) -> str:
    raw = (Path(__file__).parent.parent / "prompts" / f"{name}.txt").read_text()
    try:
        return raw.format(**vars)          # simple .format() version
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(f"Prompt '{name}' missing variable: {missing}") from None