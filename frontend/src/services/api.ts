import axios from 'axios'

const api = axios.create({baseURL:'/api'})

api.interceptors.request.use(c=>{
  const t=localStorage.getItem('studyhub_token')
  if(t)c.headers.Authorization=`Bearer ${t}`
  return c
})

export default api

export const errorMessage=(e:unknown)=>{
  if(!axios.isAxiosError(e)){
    return 'No fue posible completar la operación'
  }

  const detail=e.response?.data?.detail

  if(Array.isArray(detail)){
    const message=detail.find(
      item=>typeof item?.msg==='string'
    )?.msg

    if(message){
      return message.replace(/^Value error,\s*/i,'')
    }
  }

  if(typeof detail==='string'){
    return detail
  }

  return 'No fue posible completar la operación'
}