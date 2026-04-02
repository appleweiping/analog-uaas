from pathlib import Path

from src.circuits.netlist_writer import NetlistWriter


def test_netlist_writer_replaces_all_keys(tmp_path: Path) -> None:
    template = tmp_path / "template.scs"
    template.write_text("W_IN={w_in}\nL_IN={l_in}\nVDD={vdd}\n", encoding="utf-8")

    writer = NetlistWriter(template)
    output = tmp_path / "out.scs"
    writer.write(output, {"w_in": 1e-6, "l_in": 2e-6, "vdd": 1.8})

    text = output.read_text(encoding="utf-8")
    assert "W_IN=1e-06" in text
    assert "L_IN=2e-06" in text
    assert "VDD=1.8" in text