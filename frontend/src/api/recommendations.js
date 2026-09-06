import client from './client';

export const recommendationsApi = {
    getLearningPlans: async () => {
        const response = await client.get('/recommendations/');
        return response.data;
    },
    getLearningPlanDetail: async (planId) => {
        const response = await client.get(`/recommendations/${planId}/`);
        return response.data;
    }
};

export default recommendationsApi;
