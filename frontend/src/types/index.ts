export type User={id:number;nombre:string;apellido:string;email:string;rol:'USER'|'ADMIN';activo:boolean;created_at:string}
export type Group={id:number;nombre:string;descripcion:string;materia:string;ubicacion:string;cupo_maximo:number;creador_id:number;fecha_creacion:string;activo:boolean;member_count:number;is_member:boolean;is_owner:boolean}
export type Appointment={id:number;titulo:string;descripcion:string;fecha:string;hora_inicio:string;hora_fin:string;ubicacion:string;grupo_id:number;creador_id:number;estado:'PROGRAMADA'|'FINALIZADA'|'CANCELADA';group_name:string}
export type GroupInput={nombre:string;descripcion:string;materia:string;ubicacion:string;cupo_maximo:number;activo?:boolean}
export type AppointmentInput={titulo:string;descripcion:string;fecha:string;hora_inicio:string;hora_fin:string;ubicacion:string;grupo_id:number;estado?:string}
