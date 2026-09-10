import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api, { errorMessage } from "../services/api";
import type { Appointment, AppointmentInput, Group } from "../types";
import ConfirmModal from "../components/ConfirmModal";
import { useAuth } from '../contexts/AuthContext'

const blank: AppointmentInput = {
  titulo: "",
  descripcion: "",
  fecha: "",
  hora_inicio: "",
  hora_fin: "",
  ubicacion: "",
  grupo_id: 0,
};

export function AppointmentsPage() {
  const [items, setItems] = useState<Appointment[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [group, setGroup] = useState("");
  const [date, setDate] = useState("");

  const load = () =>
    api
      .get<Appointment[]>(
        `/appointments?${group ? `group_id=${group}&` : ""}${
          date ? `fecha=${date}` : ""
        }`
      )
      .then((r) => setItems(r.data));

  useEffect(() => {
    api.get<Group[]>("/groups").then((r) => setGroups(r.data));
    load();
  }, []);

  return (
    <>
      <header className="page-head inline">
        <div>
          <h1>Sesiones</h1>
          <p>Planifica y consulta los próximos encuentros.</p>
        </div>

        <Link className="button" to="/appointments/new">
          Nueva sesión
        </Link>
      </header>

      <div className="toolbar">
        <select value={group} onChange={(e) => setGroup(e.target.value)}>
          <option value="">Todos los grupos</option>

          {groups.map((g) => (
            <option value={g.id} key={g.id}>
              {g.nombre}
            </option>
          ))}
        </select>

        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />

        <button className="secondary" onClick={load}>
          Filtrar
        </button>
      </div>

      <div className="session-list">
        {items.map((a) => (
          <Link
            to={`/appointments/${a.id}`}
            className="session-row"
            key={a.id}
          >
            <div>
              <strong>{a.titulo}</strong>
              <span>{a.group_name}</span>
            </div>

            <div>
              {new Date(a.fecha + "T12:00").toLocaleDateString("es-GT")} ·{" "}
              {a.hora_inicio.slice(0, 5)}
            </div>

            <span className={"status " + a.estado.toLowerCase()}>
              {a.estado}
            </span>
          </Link>
        ))}
      </div>
    </>
  );
}

export function AppointmentFormPage() {
  const { id } = useParams();
  const nav = useNavigate();

  const [data, setData] = useState<AppointmentInput>(blank);
  const [groups, setGroups] = useState<Group[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get<Group[]>("/groups?mine=true").then((r) => setGroups(r.data));

    if (id) {
      api
        .get<Appointment>(`/appointments/${id}`)
        .then((r) => setData(r.data));
    }
  }, [id]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();

    setBusy(true);
    setError("");

    try {
      const r = id
        ? await api.put<Appointment>(`/appointments/${id}`, data)
        : await api.post<Appointment>("/appointments", data);

      nav(`/appointments/${r.data.id}`);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <header className="page-head">
        <h1>{id ? "Editar sesión" : "Nueva sesión"}</h1>
        <p>Define cuándo y dónde se reunirá el grupo.</p>
      </header>

      <form className="panel form" onSubmit={submit}>
        {error && <div className="notice error">{error}</div>}

        <label>
          Título
          <input
            required
            value={data.titulo}
            onChange={(e) =>
              setData({
                ...data,
                titulo: e.target.value,
              })
            }
          />
        </label>

        <label>
          Descripción
          <textarea
            rows={4}
            value={data.descripcion}
            onChange={(e) =>
              setData({
                ...data,
                descripcion: e.target.value,
              })
            }
          />
        </label>

        <div className="form-grid">
          <label>
            Grupo
            <select
              required
              value={data.grupo_id}
              onChange={(e) =>
                setData({
                  ...data,
                  grupo_id: Number(e.target.value),
                })
              }
            >
              <option value="0">Selecciona un grupo</option>

              {groups
                .filter((g) => g.is_owner)
                .map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.nombre}
                  </option>
                ))}
            </select>
          </label>

          <label>
            Fecha
            <input
              type="date"
              required
              value={data.fecha}
              onChange={(e) =>
                setData({
                  ...data,
                  fecha: e.target.value,
                })
              }
            />
          </label>

          <label>
            Inicio
            <input
              type="time"
              required
              value={data.hora_inicio}
              onChange={(e) =>
                setData({
                  ...data,
                  hora_inicio: e.target.value,
                })
              }
            />
          </label>

          <label>
            Fin
            <input
              type="time"
              required
              value={data.hora_fin}
              onChange={(e) =>
                setData({
                  ...data,
                  hora_fin: e.target.value,
                })
              }
            />
          </label>

          <label>
            Ubicación
            <input
              required
              value={data.ubicacion}
              onChange={(e) =>
                setData({
                  ...data,
                  ubicacion: e.target.value,
                })
              }
            />
          </label>
        </div>

        {id && (
          <label>
            Estado
            <select
              value={data.estado || "PROGRAMADA"}
              onChange={(e) =>
                setData({
                  ...data,
                  estado: e.target.value,
                })
              }
            >
              <option>PROGRAMADA</option>
              <option>FINALIZADA</option>
              <option>CANCELADA</option>
            </select>
          </label>
        )}

        <div className="actions">
          <button
            className="secondary"
            type="button"
            onClick={() => nav(-1)}
          >
            Cancelar
          </button>

          <button disabled={busy}>
            {busy ? "Guardando…" : "Guardar sesión"}
          </button>
        </div>
      </form>
    </>
  );
}

export function AppointmentDetailPage() {
  const { id } = useParams();
  const nav = useNavigate();

  
  const [item, setItem] = useState<Appointment | null>(null);
  const [confirm, setConfirm] = useState(false);
  const [error, setError] = useState("");
  
  const { user } = useAuth();
  const canManage = user?.rol === 'ADMIN' || item?.creador_id === user?.id
  useEffect(() => {
    api
      .get<Appointment>(`/appointments/${id}`)
      .then((r) => setItem(r.data))
      .catch((e) => setError(errorMessage(e)));
  }, [id]);

  const remove = async () => {
    try {
      await api.delete(`/appointments/${id}`);
      nav("/appointments");
    } catch (e) {
      setError(errorMessage(e));
    }
  };

  if (!item) {
    return <p>Cargando sesión…</p>;
  }

  return (
    <>
      <header className="page-head inline">
        <div>
          <span className={"status " + item.estado.toLowerCase()}>
            {item.estado}
          </span>

          <h1>{item.titulo}</h1>
          <p>{item.group_name}</p>
        </div>

        {canManage && (
        <div className="actions">
            <Link className="button secondary" to={`/appointments/${id}/edit`}>
            Editar
            </Link>
            <button className="danger" onClick={() => setConfirm(true)}>
            Eliminar
            </button>
        </div>
        )}
      </header>

      {error && <div className="notice error">{error}</div>}

      <section className="panel details">
        <p>{item.descripcion || "Sin descripción adicional."}</p>

        <dl>
          <dt>Fecha</dt>
          <dd>
            {new Date(item.fecha + "T12:00").toLocaleDateString("es-GT")}
          </dd>

          <dt>Horario</dt>
          <dd>
            {item.hora_inicio.slice(0, 5)} – {item.hora_fin.slice(0, 5)}
          </dd>

          <dt>Ubicación</dt>
          <dd>{item.ubicacion}</dd>
        </dl>
      </section>

      <ConfirmModal
        open={confirm}
        title="¿Eliminar esta sesión?"
        onCancel={() => setConfirm(false)}
        onConfirm={remove}
      />
    </>
  );
}