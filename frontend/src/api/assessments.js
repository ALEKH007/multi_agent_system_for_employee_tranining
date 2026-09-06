import client from './client';

export const assessmentsApi = {
    getAssessments: async (employeeId = null) => {
        const url = employeeId ? `/assessments/?employee_id=${employeeId}` : '/assessments/';
        const response = await client.get(url);
        return response.data;
    },
    getAssessmentDetail: async (assessmentId) => {
        const response = await client.get(`/assessments/${assessmentId}/`);
        return response.data;
    },
    submitAssessment: async (assessmentId, answers) => {
        const response = await client.post(`/assessments/${assessmentId}/submit/`, { answers });
        return response.data;
    },
    getResult: async (assessmentId) => {
        const response = await client.get(`/assessments/${assessmentId}/result/`);
        return response.data;
    }
};

export default assessmentsApi;
