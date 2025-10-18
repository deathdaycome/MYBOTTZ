import { apiClient } from './client';
import type { Project, ProjectStats } from '../types/project';

export const projectsApi = {
  // Получить все проекты пользователя
  getMyProjects: async (): Promise<Project[]> => {
    const response = await apiClient.get('/projects');
    return response.data;
  },

  // Получить один проект по ID
  getProject: async (id: number): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },

  // Получить статистику по проектам
  getProjectsStats: async (): Promise<ProjectStats> => {
    const response = await apiClient.get('/projects/stats');
    return response.data;
  },

  // Создать новый проект (быстрый запрос)
  createQuickProject: async (data: {
    project_type: string;
    title: string;
    description: string;
    budget: string;
    deadline: string;
  }): Promise<Project> => {
    const response = await apiClient.post('/projects/quick', data);
    return response.data;
  },

  // Создать проект через ТЗ
  createProjectFromTZ: async (data: {
    method: string;
    title: string;
    description: string;
    project_type: string;
    complexity: string;
    [key: string]: any;
  }): Promise<Project> => {
    const response = await apiClient.post('/projects/tz', data);
    return response.data;
  },
};
