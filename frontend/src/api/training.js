import client from './client';

export const trainingApi = {
    getMyCourses: async () => {
        const response = await client.get('/training/my-courses/');
        return response.data;
    },
    updateProgress: async (progressId, completionStatus, score = 100) => {
        const response = await client.put(`/training/progress/${progressId}/`, {
            completion_status: completionStatus,
            score: score
        });
        return response.data;
    },
    getModules: async () => {
        const response = await client.get('/training/modules/');
        return response.data;
    }
};

export default trainingApi;
