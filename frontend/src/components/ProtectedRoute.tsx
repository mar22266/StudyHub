import {Navigate} from 'react-router-dom';import type {ReactElement} from 'react';import {useAuth} from '../contexts/AuthContext'
export default function ProtectedRoute({children}:{children:ReactElement}){const{user,loading}=useAuth();if(loading)return <div className="center">Cargando StudyHub…</div>;return user?children:<Navigate to="/login" replace/>}
