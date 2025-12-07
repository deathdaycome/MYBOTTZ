// Print utilities for projects

interface Project {
  id: number
  name: string
  status?: string
  project_cost?: number
  paid_total?: number
  executor_cost?: number
  executor_paid_total?: number
  assigned_to?: { username?: string; first_name?: string }
  user?: { first_name?: string; telegram_username?: string }
  deadline?: string
  created_at?: string
  description?: string
  test_link?: string
}

export const printProjects = (projects: Project[], title: string = 'Проекты') => {
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert('Не удалось открыть окно печати. Проверьте настройки браузера.')
    return
  }

  const totalCost = projects.reduce((sum, p) => sum + (p.project_cost || 0), 0)
  const totalPaid = projects.reduce((sum, p) => sum + (p.paid_total || 0), 0)
  const totalExecutorCost = projects.reduce((sum, p) => sum + (p.executor_cost || 0), 0)
  const totalProfit = totalCost - totalExecutorCost

  const html = `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${title}</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          padding: 40px;
          color: #333;
          background: white;
        }

        .header {
          text-align: center;
          margin-bottom: 40px;
          border-bottom: 3px solid #4F46E5;
          padding-bottom: 20px;
        }

        .header h1 {
          font-size: 32px;
          color: #1F2937;
          margin-bottom: 10px;
        }

        .header .date {
          font-size: 14px;
          color: #6B7280;
        }

        .summary {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 20px;
          margin-bottom: 40px;
        }

        .summary-card {
          padding: 15px;
          border-radius: 8px;
          border: 2px solid #E5E7EB;
        }

        .summary-card.total {
          border-color: #3B82F6;
          background: #EFF6FF;
        }

        .summary-card.paid {
          border-color: #10B981;
          background: #ECFDF5;
        }

        .summary-card.executor {
          border-color: #F59E0B;
          background: #FFFBEB;
        }

        .summary-card.profit {
          border-color: #8B5CF6;
          background: #F5F3FF;
        }

        .summary-card .label {
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          color: #6B7280;
          margin-bottom: 5px;
        }

        .summary-card .value {
          font-size: 24px;
          font-weight: bold;
        }

        .summary-card.total .value { color: #3B82F6; }
        .summary-card.paid .value { color: #10B981; }
        .summary-card.executor .value { color: #F59E0B; }
        .summary-card.profit .value { color: #8B5CF6; }

        .project {
          margin-bottom: 30px;
          padding: 20px;
          border: 1px solid #E5E7EB;
          border-radius: 8px;
          page-break-inside: avoid;
        }

        .project-header {
          display: flex;
          justify-content: space-between;
          align-items: start;
          margin-bottom: 15px;
          padding-bottom: 10px;
          border-bottom: 2px solid #F3F4F6;
        }

        .project-title {
          font-size: 18px;
          font-weight: bold;
          color: #1F2937;
        }

        .project-id {
          font-size: 12px;
          color: #6B7280;
        }

        .project-status {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          background: #F3F4F6;
          color: #374151;
        }

        .project-details {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
          margin-bottom: 10px;
        }

        .detail-item {
          font-size: 13px;
        }

        .detail-label {
          font-weight: 600;
          color: #6B7280;
        }

        .detail-value {
          color: #1F2937;
        }

        .project-description {
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #E5E7EB;
          font-size: 13px;
          color: #4B5563;
          line-height: 1.6;
        }

        .footer {
          margin-top: 40px;
          padding-top: 20px;
          border-top: 3px solid #4F46E5;
          text-align: center;
          font-size: 12px;
          color: #6B7280;
        }

        @media print {
          body {
            padding: 20px;
          }

          .project {
            page-break-inside: avoid;
          }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>${title}</h1>
        <div class="date">Дата формирования: ${new Date().toLocaleString('ru-RU')}</div>
        <div class="date">Всего проектов: ${projects.length}</div>
      </div>

      <div class="summary">
        <div class="summary-card total">
          <div class="label">Общая стоимость</div>
          <div class="value">${totalCost.toLocaleString('ru-RU')} ₽</div>
        </div>
        <div class="summary-card paid">
          <div class="label">Оплачено</div>
          <div class="value">${totalPaid.toLocaleString('ru-RU')} ₽</div>
        </div>
        <div class="summary-card executor">
          <div class="label">Исполнителям</div>
          <div class="value">${totalExecutorCost.toLocaleString('ru-RU')} ₽</div>
        </div>
        <div class="summary-card profit">
          <div class="label">Прибыль</div>
          <div class="value">${totalProfit.toLocaleString('ru-RU')} ₽</div>
        </div>
      </div>

      ${projects
        .map((project, index) => {
          const remaining = (project.project_cost || 0) - (project.paid_total || 0)
          const executorRemaining = (project.executor_cost || 0) - (project.executor_paid_total || 0)
          const profit = (project.project_cost || 0) - (project.executor_cost || 0)

          return `
            <div class="project">
              <div class="project-header">
                <div>
                  <div class="project-title">${index + 1}. ${project.name || 'Без названия'}</div>
                  <div class="project-id">ID: ${project.id}</div>
                </div>
                ${project.status ? `<div class="project-status">${project.status}</div>` : ''}
              </div>

              <div class="project-details">
                <div class="detail-item">
                  <span class="detail-label">Стоимость:</span>
                  <span class="detail-value">${(project.project_cost || 0).toLocaleString('ru-RU')} ₽</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Оплачено:</span>
                  <span class="detail-value">${(project.paid_total || 0).toLocaleString('ru-RU')} ₽</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Остаток:</span>
                  <span class="detail-value">${remaining.toLocaleString('ru-RU')} ₽</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Прибыль:</span>
                  <span class="detail-value">${profit.toLocaleString('ru-RU')} ₽</span>
                </div>

                ${
                  project.executor_cost
                    ? `
                <div class="detail-item">
                  <span class="detail-label">Исполнителю:</span>
                  <span class="detail-value">${(project.executor_cost || 0).toLocaleString('ru-RU')} ₽</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Выплачено:</span>
                  <span class="detail-value">${(project.executor_paid_total || 0).toLocaleString('ru-RU')} ₽</span>
                </div>
                `
                    : ''
                }

                ${
                  project.assigned_to
                    ? `
                <div class="detail-item">
                  <span class="detail-label">Исполнитель:</span>
                  <span class="detail-value">${project.assigned_to.username || project.assigned_to.first_name}</span>
                </div>
                `
                    : ''
                }

                ${
                  project.user
                    ? `
                <div class="detail-item">
                  <span class="detail-label">Клиент:</span>
                  <span class="detail-value">${project.user.first_name || project.user.telegram_username || 'Не указан'}</span>
                </div>
                `
                    : ''
                }

                ${
                  project.deadline
                    ? `
                <div class="detail-item">
                  <span class="detail-label">Дедлайн:</span>
                  <span class="detail-value">${new Date(project.deadline).toLocaleDateString('ru-RU')}</span>
                </div>
                `
                    : ''
                }

                ${
                  project.created_at
                    ? `
                <div class="detail-item">
                  <span class="detail-label">Создан:</span>
                  <span class="detail-value">${new Date(project.created_at).toLocaleDateString('ru-RU')}</span>
                </div>
                `
                    : ''
                }
              </div>

              ${
                project.description
                  ? `
              <div class="project-description">
                <strong>Описание:</strong><br>
                ${project.description.replace(/\n/g, '<br>')}
              </div>
              `
                  : ''
              }
            </div>
          `
        })
        .join('')}

      <div class="footer">
        <p>Отчет сформирован автоматически системой CRM</p>
      </div>

      <script>
        window.onload = () => {
          window.print();
        };
      </script>
    </body>
    </html>
  `

  printWindow.document.write(html)
  printWindow.document.close()
}

export const printSingleProject = (project: Project) => {
  printProjects([project], `Проект: ${project.name}`)
}
