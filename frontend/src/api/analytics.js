import client from './client';

export const analyticsApi = {
    getDashboardMetrics: async () => {
        const response = await client.get('/analytics/dashboard/');
        return response.data;
    },
    getDepartmentMetrics: async (departmentId = 'all') => {
        const response = await client.get(`/analytics/department/${departmentId}/`);
        return response.data;
    },
    getReports: async () => {
        const response = await client.get('/analytics/reports/');
        return response.data;
    }
};

export default analyticsApi;
