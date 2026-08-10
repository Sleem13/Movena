import { selectTemporalModel } from "@/src/api/recognition";

describe("recognition model selection", () => {
  it("selects only an active, integrity-verified temporal model", () => {
    const selected = selectTemporalModel([
      { model_id: "frame", model_name: "frame", artifact_format: "xgboost_json", status: "candidate", active: true, integrity_status: "valid" },
      { model_id: "bad-temporal", model_name: "gru", artifact_format: "torchscript_sequence", status: "candidate", active: true, integrity_status: "invalid" },
      { model_id: "good-temporal", model_name: "gru", artifact_format: "torchscript_sequence", status: "candidate", active: true, integrity_status: "valid" },
    ]);
    expect(selected?.model_id).toBe("good-temporal");
  });

  it("fails closed when no valid temporal model is active", () => {
    expect(selectTemporalModel([{ model_id: "frame", model_name: "frame", artifact_format: "xgboost_json", status: "candidate", active: true, integrity_status: "valid" }])).toBeNull();
  });
});
