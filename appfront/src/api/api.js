import axiosInstance from "./index"

const axios = axiosInstance

export const getBooks = () => {
    return axios.get('http://localhost:8000/api/books/')
}

export const postBook = (bookName, bookAuthor) => {
    return axios.post('http://localhost:8000/api/books/',
        {
            'name': bookName,
            'author': bookAuthor
        }
    )
}

export const uploadFiles = (formData) => {
    return axios.post('http://localhost:8000/api/files/', formData,
        {
           headers: {
            'Content-Type': 'multipart/form-data'
           }
        }
    )
}

export const submitInputText = (text) => {
    return axios.post('http://localhost:8000/api/files/',
        {
            text: text
        }
    )
}
