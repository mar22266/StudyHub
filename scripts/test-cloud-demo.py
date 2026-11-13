"""Pruebas HTTP con cuentas demo privadas y limpieza de registros temporales."""
import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
import httpx

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credentials', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT/'deployment-evidence/actualizacion/cloud-tests.json')
    args = parser.parse_args()
    private = json.loads(args.credentials.read_text())
    results = []
    with httpx.Client(base_url=private['url'], timeout=60) as client:
        def check(name, method, path, expected, token=None, **kwargs):
            headers = {'Authorization': 'Bearer '+token} if token else {}
            response = client.request(method, path, headers=headers, **kwargs)
            results.append({'case': name, 'expected': expected, 'actual': response.status_code,
                            'passed': response.status_code == expected})
            if response.status_code != expected:
                raise RuntimeError(f'{name}: HTTP {response.status_code}, esperado {expected}')
            return response.json() if response.content else None

        tokens = {}
        for email, password in private['accounts'].items():
            login = check('login '+email.split('@')[0], 'POST', '/api/auth/login', 200,
                          json={'email': email, 'password': password})
            tokens[email.split('@')[0]] = login['access_token']
            me = check('perfil '+email.split('@')[0], 'GET', '/api/auth/me', 200, login['access_token'])
            assert me['email'] == email
        ana, carlos = tokens['ana'], tokens['carlos']
        check('rechazo sin autenticación', 'GET', '/api/groups', 401)
        check('clave incorrecta', 'POST', '/api/auth/login', 401,
              json={'email': 'ana@studyhub.local', 'password': secrets.token_urlsafe(24)})
        groups = check('grupos demo', 'GET', '/api/groups', 200, ana)
        assert len(groups) == 5
        check('sesiones demo', 'GET', '/api/appointments', 200, ana)
        search = check('búsqueda parametrizada', 'GET', '/api/groups/search', 200, ana,
                       params={'q': "' OR 1=1 --"})
        assert search == []
        owned = next(g for g in groups if g['is_owner'])
        payload = {k: owned[k] for k in ('nombre','descripcion','materia','ubicacion','cupo_maximo','activo')}
        check('bloqueo de edición ajena', 'PUT', f"/api/groups/{owned['id']}", 403, carlos, json=payload)
        group_id = appointment_id = None
        try:
            payload = {'nombre': 'Prueba nube '+secrets.token_hex(4), 'descripcion': 'Registro temporal de verificación',
                       'materia': 'DevOps', 'ubicacion': 'Nube', 'cupo_maximo': 5}
            group = check('crear grupo', 'POST', '/api/groups', 201, ana, json=payload)
            group_id = group['id']
            check('actualizar grupo', 'PUT', f'/api/groups/{group_id}', 200, ana,
                  json={**payload, 'nombre': payload['nombre']+' actualizado', 'activo': True})
            appointment = check('crear sesión', 'POST', '/api/appointments', 201, ana,
                json={'titulo':'Verificación temporal', 'descripcion':'Prueba HTTP',
                      'fecha':str(date.today()+timedelta(days=2)), 'hora_inicio':'10:00:00',
                      'hora_fin':'11:00:00','ubicacion':'Nube','grupo_id':group_id})
            appointment_id = appointment['id']
        finally:
            if appointment_id is not None:
                check('eliminar sesión temporal', 'DELETE', f'/api/appointments/{appointment_id}', 204, ana)
            if group_id is not None:
                check('eliminar grupo temporal', 'DELETE', f'/api/groups/{group_id}', 204, ana)
        assert len(check('grupos tras limpieza', 'GET', '/api/groups', 200, ana)) == 5
        ready = check('PostgreSQL disponible', 'GET', '/api/ready', 200)
        report = {'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'url':private['url'],
                  'commit':ready.get('commit') or ready.get('sha'), 'ready':ready, 'results':results,
                  'all_passed':all(r['passed'] for r in results), 'temporary_records_removed':True}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
        print(json.dumps({'all_passed': report['all_passed'], 'cases':len(results), 'ready':ready}))


if __name__ == '__main__':
    main()
