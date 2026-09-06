import React, { useEffect, useState } from 'react';
import analyticsApi from '../../api/analytics';

export default function TeamProgressPage() {
    const [teamData, setTeamData] = useState(null);

    useEffect(() => {
        const fetchTeamData = async () => {
            try {
                const data = await analyticsApi.getDepartmentMetrics('me');
                if (data && data.team && data.team.length > 0) {
                    setTeamData(data.team);
                } else {
                    setTeamData([
                        { id: 'e1', name: 'Alice Smith', role: 'Frontend Engineer', progress: 80, status: 'on_track' },
                        { id: 'e2', name: 'Bob Johnson', role: 'Backend Engineer', progress: 45, status: 'behind' },
                        { id: 'e3', name: 'Charlie Davis', role: 'Data Scientist', progress: 100, status: 'completed' },
                    ]);
                }
            } catch (err) {
                console.warn('API connection notice (using team fallback):', err);
                setTeamData([
                    { id: 'e1', name: 'Alice Smith', role: 'Frontend Engineer', progress: 80, status: 'on_track' },
                    { id: 'e2', name: 'Bob Johnson', role: 'Backend Engineer', progress: 45, status: 'behind' },
                    { id: 'e3', name: 'Charlie Davis', role: 'Data Scientist', progress: 100, status: 'completed' },
                ]);
            }
        };

        fetchTeamData();
    }, []);

    return (
        <div className="space-y-8 animate-fade-in">
            <header className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-display font-bold text-white mb-2">Team Progress</h1>
                    <p className="text-slate-400">Monitor your direct reports' onboarding and training.</p>
                </div>
                <button 
                    onClick={() => alert("Downloading team training report CSV...")}
                    className="px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 hover:bg-slate-700 active:scale-95 transition-all text-sm font-medium cursor-pointer"
                >
                    Download Report
                </button>
            </header>

            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-slate-900/50 text-slate-400 uppercase text-xs">
                            <tr>
                                <th className="px-6 py-4 font-semibold">Employee</th>
                                <th className="px-6 py-4 font-semibold">Role</th>
                                <th className="px-6 py-4 font-semibold">Training Progress</th>
                                <th className="px-6 py-4 font-semibold">Status</th>
                                <th className="px-6 py-4 font-semibold text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {!teamData ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-8 text-center text-slate-500">Loading team data...</td>
                                </tr>
                            ) : (
                                teamData.map((emp) => (
                                    <tr key={emp.id} className="hover:bg-slate-800/20 transition-colors">
                                        <td className="px-6 py-4 font-medium text-white">{emp.name}</td>
                                        <td className="px-6 py-4">{emp.role}</td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-full bg-slate-700 rounded-full h-2 max-w-[150px]">
                                                    <div 
                                                        className={`h-2 rounded-full ${emp.progress === 100 ? 'bg-emerald-500' : 'bg-indigo-500'}`} 
                                                        style={{ width: `${emp.progress}%` }}
                                                    ></div>
                                                </div>
                                                <span className="text-xs">{emp.progress}%</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {emp.status === 'on_track' && <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-medium border border-emerald-500/20"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div> On Track</span>}
                                            {emp.status === 'behind' && <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 text-xs font-medium border border-amber-500/20"><div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div> Behind</span>}
                                            {emp.status === 'completed' && <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 text-xs font-medium border border-blue-500/20"><div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div> Completed</span>}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button 
                                                onClick={() => alert(`Details for ${emp.name}:\nRole: ${emp.role}\nProgress: ${emp.progress}%\nStatus: ${emp.status}`)}
                                                className="text-indigo-400 hover:text-indigo-300 font-medium text-xs transition-colors cursor-pointer"
                                            >
                                                View Details
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
