from scripts import (
    fm,
    gen_raw_acquisition,
    gen_settings,
    gen_readings,
    gen_total_dc_current,
    load_data,
)


if __name__ == "__main__":
    sheet_file = "../documentation/SSAStorageRing/Variáveis Aquisição Anel.xlsx"

    entries = load_data(file_name=sheet_file)
    gen_raw_acquisition()
    gen_settings(entries=entries)
    gen_readings(entries=entries)
    gen_total_dc_current(entries=entries)
    fm.close()
