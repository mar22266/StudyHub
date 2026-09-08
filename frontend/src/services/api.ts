import axios from 'axios'
const api=axios.create({baseURL:'/api'})
api.interceptors.request.use(c=>{const t=localStorage.getItem('studyhub_token');if(t)c.headers.Authorization=`Bearer ${t}`;return c})
export default api
export const errorMessage=(e:unknown)=>axios.isAxiosError(e)?(e.response?.data?.detail||'No fue posible completar la operación'):'No fue posible completar la operación'
