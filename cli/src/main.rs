use std::{env, fs, path::PathBuf, process};

use serde_json::json;

fn usage() -> ! {
    eprintln!("usage: lp0003-cli safe-lane-evidence --out <path>");
    process::exit(2);
}

fn main() {
    let mut args = env::args().skip(1);
    let Some(command) = args.next() else { usage() };
    match command.as_str() {
        "safe-lane-evidence" => write_safe_lane_evidence(args.collect()),
        _ => usage(),
    }
}

fn write_safe_lane_evidence(args: Vec<String>) {
    let mut out: Option<PathBuf> = None;
    let mut iter = args.into_iter();
    while let Some(arg) = iter.next() {
        match arg.as_str() {
            "--out" => {
                let Some(path) = iter.next() else { usage() };
                out = Some(PathBuf::from(path));
            }
            _ => usage(),
        }
    }
    let Some(out_path) = out else { usage() };
    let report = match lp0003_sdk::run_two_distribution_demo() {
        Ok(report) => report,
        Err(err) => {
            eprintln!("safe-lane evidence generation failed: {err}");
            process::exit(1);
        }
    };
    let payload = json!({
        "distribution_count": report.distribution_count,
        "unique_claim_count": report.unique_claim_count,
        "duplicate_rejections_observed": report.duplicate_rejections_observed,
        "evidence_source": "safe-lane",
        "final_evidence": false,
        "status": report.status,
        "note": "Local deterministic SDK relation evidence only. This file is intentionally rejected by final-publication-check.py as final LEZ/RISC0 evidence."
    });
    if let Some(parent) = out_path.parent() {
        if let Err(err) = fs::create_dir_all(parent) {
            eprintln!("failed to create output directory: {err}");
            process::exit(1);
        }
    }
    let text = serde_json::to_string_pretty(&payload).expect("serialize JSON") + "\n";
    if let Err(err) = fs::write(&out_path, text) {
        eprintln!("failed to write {}: {err}", out_path.display());
        process::exit(1);
    }
    println!("wrote safe-lane evidence: {}", out_path.display());
}
