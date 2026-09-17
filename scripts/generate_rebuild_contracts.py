"""Generate shared contracts/tokens from existing schemas; no app startup imports."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.schemas.auth_schema import (CurrentUserResponse, UserLoginRequest, TokenResponse,
    UserRegisterRequest, UserSummary, EmailRequest, TokenRequest, PasswordResetRequest, AuthMessageResponse)
from app.schemas.care_schema import (PatientTodayResponse, AdherenceCreate, AdherenceDetail, ExerciseResponseReview,
    AppointmentCreate, AppointmentSummary, AppointmentUpdate, AppointmentJoinResponse, AvailabilityCreate, AvailabilityDetail,
    PatientHealthProfileUpdate, NotificationSummary, ClinicalNoteCreate, ClinicalNoteDetail)
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date, datetime
from app.schemas.analysis_job_schema import AnalysisJobResponse as LegacyAnalysisJobResponse
from app.schemas.patient_schema import ExercisePlanCreate, ExercisePlanDetail, ExercisePlanStatusUpdate
from app.schemas.session_schema import SessionListResponse, SessionDetail
from app.exercises.metadata import list_exercise_metadata

class AnalysisJobResponse(LegacyAnalysisJobResponse):
    # Compatibility lineage is known; historical task-model versions may not be.
    engine_version: str | None = None
    model_version: str | None = None

class AppointmentSlot(BaseModel):
    starts_at: datetime
    ends_at: datetime

class AvailabilitySlots(BaseModel):
    therapist_user_id: str
    date: date
    slots: list[AppointmentSlot]

class PatientHealthProfile(PatientHealthProfileUpdate):
    patient_id: str

class ConsentRecord(BaseModel):
    consent_type: str
    accepted: bool
    accepted_at: datetime | None = None
    version: str

class ProgressReportSummary(BaseModel):
    progress_report_id: str
    period_start: date
    period_end: date
    created_at: datetime
    download_url: str

class ProgressReportCreateResponse(BaseModel):
    progress_report_id: str
    download_url: str
    shared_with_patient: bool

class DataRightsCreate(BaseModel):
    request_type: Literal['export', 'correction', 'deletion']
    details: str | None = Field(default=None, max_length=2000)

class DataRightsRecord(BaseModel):
    request_id: str
    request_type: Literal['export', 'correction', 'deletion']
    status: str
    details: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    reviewed_at: datetime | None = None
    retention_until: datetime | None = None
    account_id: str | None = None
    account_email: str | None = None
    account_name: str | None = None

class DataRightsReview(BaseModel):
    decision: Literal['approve', 'reject']
    reason: str = Field(min_length=3, max_length=2000)

MODELS = [ClinicalNoteCreate, ClinicalNoteDetail, SessionListResponse, SessionDetail, PatientHealthProfileUpdate, PatientHealthProfile, ConsentRecord, ProgressReportSummary, ProgressReportCreateResponse, DataRightsCreate, DataRightsRecord, DataRightsReview, NotificationSummary,
          ExercisePlanCreate, ExercisePlanDetail, ExercisePlanStatusUpdate,
          UserRegisterRequest, UserSummary, EmailRequest, TokenRequest, PasswordResetRequest, AuthMessageResponse,
          AppointmentCreate, AppointmentSummary, AppointmentUpdate, AppointmentJoinResponse,
          AvailabilityCreate, AvailabilityDetail, AvailabilitySlots, CurrentUserResponse, UserLoginRequest, TokenResponse, PatientTodayResponse,
          AdherenceCreate, AdherenceDetail, ExerciseResponseReview, AnalysisJobResponse]


def ts_type(schema):
    if '$ref' in schema:
        return schema['$ref'].split('/')[-1]
    if 'anyOf' in schema:
        return ' | '.join(ts_type(s) for s in schema['anyOf'])
    if 'enum' in schema:
        return ' | '.join(json.dumps(s) for s in schema['enum'])
    kind = schema.get('type')
    if kind == 'array':
        return f"Array<{ts_type(schema.get('items', {}))}>"
    if kind == 'object':
        return 'Record<string, unknown>'
    return {'string': 'string', 'integer': 'number', 'number': 'number', 'boolean': 'boolean', 'null': 'null'}.get(kind, 'unknown')


def dart_shape(schema, schemas):
    if 'anyOf' in schema:
        return dart_shape(next((s for s in schema['anyOf'] if s.get('type') != 'null'), {}), schemas)
    if '$ref' in schema:
        name = schema['$ref'].split('/')[-1]
        return (name, 'model') if 'properties' in schemas[name] else dart_shape(schemas[name], schemas)
    if schema.get('type') == 'array':
        return f"List<{dart_shape(schema.get('items', {}), schemas)[0]}>", 'array'
    return {'string': ('String', 'scalar'), 'integer': ('int', 'scalar'), 'number': ('double', 'number'),
            'boolean': ('bool', 'scalar'), 'object': ('Map<String, dynamic>', 'object')}.get(schema.get('type'), ('dynamic', 'scalar'))


def dart_read(schema, expression, schemas):
    if 'anyOf' in schema:
        return dart_read(next((s for s in schema['anyOf'] if s.get('type') != 'null'), {}), expression, schemas)
    name, kind = dart_shape(schema, schemas)
    if kind == 'model': return f'{name}.fromJson(Map<String, dynamic>.from({expression} as Map))'
    if kind == 'number': return f'({expression} as num).toDouble()'
    if kind == 'object': return f'Map<String, dynamic>.from({expression} as Map)'
    if kind == 'array': return f"({expression} as List).map((value) => {dart_read(schema.get('items', {}), 'value', schemas)}).toList()"
    return f'{expression} as {name}'


def generate():
    schemas = {}
    for model in MODELS:
        schema = model.model_json_schema(ref_template='#/components/schemas/{model}')
        schemas.update(schema.pop('$defs', {}))
        schemas[model.__name__] = schema
    operations = [
        ('/patient/appointments/{appointment_id}/session-notes', 'get', 'getPatientVisitNotes', None, 'ClinicalNoteDetail[]'),
        ('/therapist/appointments/{appointment_id}/session-notes', 'get', 'getStaffVisitNotes', None, 'ClinicalNoteDetail[]'),
        ('/therapist/appointments/{appointment_id}/session-notes', 'post', 'createVisitNote', 'ClinicalNoteCreate', 'ClinicalNoteDetail'),
        ('/sessions', 'get', 'getSessionPage', None, 'SessionListResponse'),
        ('/sessions/{session_id}', 'get', 'getSession', None, 'SessionDetail'),
        ('/auth/me', 'get', 'getCurrentUser', None, 'CurrentUserResponse'),
        ('/auth/login', 'post', 'login', 'UserLoginRequest', 'TokenResponse'),
        ('/auth/register', 'post', 'register', 'UserRegisterRequest', 'UserSummary'),
        ('/auth/forgot-password', 'post', 'forgotPassword', 'EmailRequest', 'AuthMessageResponse'),
        ('/auth/reset-password', 'post', 'resetPassword', 'PasswordResetRequest', 'AuthMessageResponse'),
        ('/auth/verify-email', 'post', 'verifyEmail', 'TokenRequest', 'AuthMessageResponse'),
        ('/auth/resend-verification', 'post', 'resendVerification', 'EmailRequest', 'AuthMessageResponse'),
        ('/patient/today', 'get', 'getToday', None, 'PatientTodayResponse'),
        ('/patient/health-profile', 'get', 'getHealthProfile', None, 'PatientHealthProfile'),
        ('/patient/health-profile', 'patch', 'updateHealthProfile', 'PatientHealthProfileUpdate', 'PatientHealthProfile'),
        ('/patient/consents', 'get', 'getConsents', None, 'ConsentRecord[]'),
        ('/patient/data-rights-requests', 'get', 'getDataRightsRequests', None, 'DataRightsRecord[]'),
        ('/patient/data-rights-requests', 'post', 'createDataRightsRequest', 'DataRightsCreate', 'DataRightsRecord'),
        ('/admin/platform/data-rights-requests', 'get', 'getDataRightsQueue', None, 'DataRightsRecord[]'),
        ('/admin/platform/data-rights-requests/{request_id}', 'patch', 'reviewDataRightsRequest', 'DataRightsReview', 'DataRightsRecord'),
        ('/patient/notifications', 'get', 'getNotifications', None, 'NotificationSummary[]'),
        ('/patient/notifications/{notification_id}/read', 'post', 'readNotification', None, 'NotificationSummary'),
        ('/patient/reports', 'get', 'getPatientReports', None, 'ProgressReportSummary[]'),
        ('/therapist/patients/{patient_id}/reports', 'post', 'createProgressReport', None, 'ProgressReportCreateResponse'),
        ('/patient/adherence', 'post', 'saveCheckIn', 'AdherenceCreate', 'AdherenceDetail'),
        ('/analysis-jobs/{job_id}', 'get', 'getAnalysisJob', None, 'AnalysisJobResponse'),
        ('/analysis-jobs', 'get', 'getActiveAnalysisJobs', None, 'AnalysisJobResponse[]'),
        ('/patient/appointments', 'get', 'getPatientAppointments', None, 'AppointmentSummary[]'),
        ('/therapist/appointments', 'get', 'getStaffAppointments', None, 'AppointmentSummary[]'),
        ('/scheduling/appointments', 'post', 'bookAppointment', 'AppointmentCreate', 'AppointmentSummary'),
        ('/scheduling/appointments/{appointment_id}', 'patch', 'updateAppointment', 'AppointmentUpdate', 'AppointmentSummary'),
        ('/scheduling/appointments/{appointment_id}/join', 'get', 'joinAppointment', None, 'AppointmentJoinResponse'),
        ('/scheduling/availability', 'get', 'getAvailableSlots', None, 'AvailabilitySlots'),
        ('/therapist/availability', 'get', 'getAvailability', None, 'AvailabilityDetail[]'),
        ('/therapist/availability', 'post', 'addAvailability', 'AvailabilityCreate', 'AvailabilityDetail'),
        ('/therapist/patients/{patient_id}/exercise-plans', 'get', 'getPlans', None, 'ExercisePlanDetail[]'),
        ('/therapist/patients/{patient_id}/exercise-plans', 'post', 'createPlan', 'ExercisePlanCreate', 'ExercisePlanDetail'),
        ('/therapist/patients/{patient_id}/exercise-plans/{plan_id}', 'patch', 'updatePlanStatus', 'ExercisePlanStatusUpdate', 'ExercisePlanDetail'),
    ]
    queries = {'getAvailableSlots': ['therapist_user_id', 'day'], 'getSessionPage': ['limit', 'offset', 'status'],
               'createProgressReport': ['period_start', 'period_end', 'share_with_patient']}
    query_schemas = {
        'limit': {'type': 'integer', 'minimum': 1, 'maximum': 200, 'default': 50},
        'offset': {'type': 'integer', 'minimum': 0, 'default': 0},
        'status': {'type': 'string', 'description': 'Empty includes every historical outcome.'},
        'share_with_patient': {'type': 'boolean', 'default': False},
    }
    keyed = {'saveCheckIn', 'bookAppointment', 'createPlan', 'createVisitNote', 'createDataRightsRequest'}
    def response_schema(name):
        schema = {'$ref': '#/components/schemas/' + name.removesuffix('[]')}
        return {'type': 'array', 'items': schema} if name.endswith('[]') else schema
    def parameter_names(path, name):
        return re.findall(r'{(\w+)}', path) + queries.get(name, [])
    def camel(value):
        return value.split('_')[0] + ''.join(part.title() for part in value.split('_')[1:])
    paths = {}
    for path, method, name, request, response in operations:
        op = {'operationId': name, 'security': [] if name in {'login','register','forgotPassword','resetPassword','verifyEmail','resendVerification'} else [{'bearerAuth': []}],
              'responses': {'201' if name in {'register','saveCheckIn','bookAppointment','addAvailability','createPlan','createVisitNote','createDataRightsRequest'} else '200': {
                  'description': 'Successful response', 'content': {'application/json': {'schema': response_schema(response)}}},
                  **{str(code): {'description': description} for code, description in [(401, 'Authentication expired or missing'),
                     (403, 'Operation or object access denied'), (409, 'Conflicting or unresolved submission'), (422, 'Invalid input'), (503, 'Dependency unavailable')]}}}
        parameters = [{'name': value, 'in': 'query' if value in queries.get(name, []) else 'path',
                       'required': name != 'getSessionPage', 'schema': query_schemas.get(value, {'type': 'string'})} for value in parameter_names(path, name)]
        if name in keyed:
            parameters.append({'name': 'Idempotency-Key', 'in': 'header', 'required': name in {'bookAppointment','createPlan','createVisitNote'}, 'schema': {'type': 'string', 'maxLength': 128}})
        if parameters: op['parameters'] = parameters
        if request:
            op['requestBody'] = {'required': True, 'content': {'application/json': {'schema': response_schema(request)}}}
        paths.setdefault('/api/v2' + path, {})[method] = op
    document = {'openapi': '3.1.0', 'info': {'title': 'Movena replacement core contracts', 'version': '2.0.0-alpha.1',
        'description': 'Typed initial recovery slice. Other compatibility endpoints remain inventoried in baseline.json.'},
        'paths': paths, 'components': {'schemas': schemas, 'securitySchemes': {'bearerAuth': {'type': 'http', 'scheme': 'bearer'}}}}
    target = ROOT / 'packages/contracts'
    # Preserved from the existing product's exerciseText catalog; do not silently
    # substitute English when a new exercise lacks its Arabic label.
    arabic_names = json.loads((target / 'exercise-names-ar.json').read_text(encoding='utf-8'))
    exercises = {entry.exercise_id: {
        'en': entry.display_name,
        'ar': entry.localized_ar.get('display_name') or arabic_names[entry.exercise_id],
    } for entry in list_exercise_metadata()}
    (target / 'exercise-names.json').write_text(json.dumps(exercises, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (target / 'openapi.json').write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    output = ['// Generated by scripts/generate_rebuild_contracts.py. Do not edit.']
    for name, schema in sorted(schemas.items()):
        if schema.get('type') == 'object' and 'properties' in schema:
            output.append(f'export interface {name} {{')
            for field, definition in schema['properties'].items():
                optional = '' if field in schema.get('required', []) else '?'
                output.append(f'  {field}{optional}: {ts_type(definition)};')
            output.append('}')
        else:
            output.append(f'export type {name} = {ts_type(schema)};')
    (target / 'generated.ts').write_text('\n'.join(output) + '\n', encoding='utf-8')
    ts_client = ["// Generated by scripts/generate_rebuild_contracts.py.",
        "import type * as Models from './generated';",
        "export type Transport = <T>(path:string, init?:RequestInit) => Promise<T>;",
        "export function coreClient(transport:Transport) { return {"]
    for path, method, name, request, response in operations:
        args = [camel(value) + (':number' if value in {'limit', 'offset'} else ':boolean' if value == 'share_with_patient' else ':string') for value in parameter_names(path, name)]
        if request: args.append(f'body:Models.{request}')
        if name in keyed: args.append('idempotencyKey:string')
        route = re.sub(r'{(\w+)}', lambda m: '${encodeURIComponent(' + camel(m[1]) + ')}', path.lstrip('/'))
        if name in queries: route += '?' + '&'.join(value + '=${encodeURIComponent(' + camel(value) + ('.toString()' if value == 'share_with_patient' else '') + ')}' for value in queries[name])
        init = f", {{method:'{method.upper()}',body:JSON.stringify(body)" + (",headers:{'Idempotency-Key':idempotencyKey}" if name in keyed else '') + '}' if request else (f", {{method:'{method.upper()}'}}" if method != 'get' else '')
        ts_client.append(f"  {name}: ({', '.join(args)}) => transport<Models.{response}>(`{route}`{init}),")
    ts_client.append('}; }')
    (target / 'client.ts').write_text('\n'.join(ts_client) + '\n')
    tokens = json.loads((target / 'design-tokens.json').read_text())
    css = ['/* Generated from packages/contracts/design-tokens.json. */']
    for mode, colors in tokens['colors'].items():
        css.append((':root' if mode == 'light' else 'html[data-theme="dark"]') + '{')
        css.extend(f'  --{key}:{value};' for key, value in colors.items())
        css.append('}')
    (ROOT / 'apps/web/src/app/tokens.css').write_text('\n'.join(css) + '\n')
    dart = ROOT / 'apps/native/lib/generated'
    dart.mkdir(parents=True, exist_ok=True)
    (dart / 'exercise_names.dart').write_text('// Generated; do not edit.\nconst exerciseNames = ' + json.dumps(exercises, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    dart_models = ['// Generated by scripts/generate_rebuild_contracts.py. Do not edit.']
    for name, schema in sorted(schemas.items()):
        if 'properties' not in schema: continue
        dart_models.extend([f'class {name} {{', '  final Map<String, dynamic> json;',
            f'  {name}.fromJson(Map<String, dynamic> value) : json = Map.unmodifiable(value) {{'])
        for field in schema.get('required', []):
            dart_models.append(f"    if (!value.containsKey('{field}')) {{ throw FormatException('Missing {field}'); }}")
        if schema.get('required'):
            dart_models.append('  }')
        else:
            dart_models[-1] = dart_models[-1].removesuffix(' {') + ';'
        dart_models.append('  Map<String, dynamic> toJson() => Map.of(json);')
        for field, definition in schema['properties'].items():
            nullable = field not in schema.get('required', []) or any(s.get('type') == 'null' for s in definition.get('anyOf', []))
            datatype = dart_shape(definition, schemas)[0] + ('?' if nullable and dart_shape(definition, schemas)[0] != 'dynamic' else '')
            getter = field.split('_')[0] + ''.join(word.title() for word in field.split('_')[1:])
            read = dart_read(definition, f"json['{field}']", schemas)
            dart_models.append(f"  {datatype} get {getter} => " + (f"json['{field}'] == null ? null : " if nullable else '') + read + ';')
        dart_models.append('}')
    (dart / 'models.dart').write_text('\n'.join(dart_models) + '\n')
    client = ["// Generated by scripts/generate_rebuild_contracts.py.", "import 'models.dart';",
              "typedef Transport = Future<dynamic> Function(String path, {String method, Object? body, String? idempotencyKey});",
              "class CoreApi { final Transport request; CoreApi(this.request);"]
    for path, method, name, request, response in operations:
        args = [('int ' if value in {'limit', 'offset'} else 'bool ' if value == 'share_with_patient' else 'String ') + camel(value) for value in parameter_names(path, name)]
        if request: args.append(f'{request} body')
        if name in keyed: args.append('String idempotencyKey')
        route = re.sub(r'{(\w+)}', lambda m: '${Uri.encodeComponent(' + camel(m[1]) + ')}', path.lstrip('/'))
        if name in queries: route += '?' + '&'.join(value + '=${Uri.encodeComponent(' + camel(value) + ('.toString()' if value in {'limit', 'offset', 'share_with_patient'} else '') + ')}' for value in queries[name])
        init = f", method: '{method.upper()}', body: body.toJson()" + (', idempotencyKey: idempotencyKey' if name in keyed else '') if request else (f", method: '{method.upper()}'" if method != 'get' else '')
        expression = f"await request('{route}'{init})"
        if response.endswith('[]'):
            model = response[:-2]
            declaration = f'List<{model}>'
            decode = f'({expression} as List).map((value) => {model}.fromJson(Map<String, dynamic>.from(value as Map))).toList()'
        else:
            declaration = response
            decode = f'{response}.fromJson(Map<String, dynamic>.from({expression} as Map))'
        client.append(f"  Future<{declaration}> {name}({', '.join(args)}) async => {decode};")
    client.append('}')
    (dart / 'client.dart').write_text('\n'.join(client) + '\n')
    messages = json.loads((target / 'messages.json').read_text(encoding='utf-8'))
    if set(messages['en']) != set(messages['ar']):
        raise ValueError('Translation catalogs must have identical keys')
    # JSON map literals are also valid Dart constant map literals.
    (dart / 'messages.dart').write_text('// Generated; do not edit.\nconst messages = ' + json.dumps(messages, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    (dart / 'tokens.dart').write_text('// Generated; do not edit.\nconst designTokens = ' + json.dumps(tokens, indent=2) + ';\n')
    print(f'Generated {len(schemas)} schemas, TypeScript types, CSS tokens, Dart tokens and translations.')


if __name__ == '__main__':
    generate()
