export function notePayload(data) {
  return {summary:String(data.get('summary') ?? '').trim(),
    recommendations:String(data.get('recommendations') ?? '').trim() || null,
    patient_visible:data.get('patient_visible') === 'on'};
}
export function uncertainNote(status) { return status === 0 || status === 409 || status >= 500; }
