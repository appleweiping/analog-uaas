def simulate(x_raw: dict) -> dict:
    # temporary mock for stage-1 pipeline validation
    gain_db = 50 + x_raw["W_in"] / 1e-6 * 0.5
    gbw_hz = 5e5 + x_raw["I_bias"] / 1e-6 * 5e4
    phase_margin_deg = 55 + x_raw["Cc"] / 1e-12 * 3
    power_w = x_raw["I_bias"] * 1.8

    return {
        "gain_db": float(gain_db),
        "gbw_hz": float(gbw_hz),
        "phase_margin_deg": float(phase_margin_deg),
        "power_w": float(power_w),
    }