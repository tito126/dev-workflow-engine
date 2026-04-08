#!/usr/bin/env node
/**
 * TFS Query Command Line Tool
 * 卫宁健康 WINNING-6.0 团队
 *
 * 命令行查询工具，用于快速查询 TFS 工作项
 */

import TFSClient, {
  findProjectCollection,
  getCollections,
  getDefaultCollection,
  setDefaultCollection
} from './tfs-client.mjs';
import readline from 'readline';

/**
 * 格式化输出工作项
 */
function formatWorkItem(workItem) {
  const id = workItem.id;
  const title = workItem.fields['System.Title'] || '无标题';
  const state = workItem.fields['System.State'] || '未知';
  const assignedTo = workItem.fields['System.AssignedTo']?.displayName || '未分配';
  const type = workItem.fields['System.WorkItemType'] || '';
  const project = workItem.fields['System.TeamProject'] || '';

  return `[${id}] ${title}\n    类型: ${type} | 状态: ${state} | 分配给: ${assignedTo} | 项目: ${project}`;
}

/**
 * 格式化输出工作项（表格格式）
 */
function formatWorkItemTable(workItems) {
  if (workItems.length === 0) {
    console.log('未找到工作项');
    return;
  }

  console.log(`\n找到 ${workItems.length} 个工作项:\n`);

  workItems.forEach(wi => {
    const id = String(wi.id).padEnd(8);
    const state = (wi.fields['System.State'] || '未知').padEnd(12);
    const type = (wi.fields['System.WorkItemType'] || '').padEnd(12);
    const title = wi.fields['System.Title'] || '无标题';
    const assignedTo = wi.fields['System.AssignedTo']?.displayName || '未分配';

    console.log(`${id} [${state}] [${type}] ${title}`);
    console.log(`    分配给: ${assignedTo}`);
    console.log();
  });
}

/**
 * 为项目选择合适的客户端（自动切换到项目所在的集合）
 */
async function getClientForProject(projectName) {
  // 首先查找项目所在的集合
  const collectionInfo = findProjectCollection(projectName);
  if (collectionInfo) {
    const client = new TFSClient(collectionInfo.collectionName);
    return client;
  }

  // 项目不存在
  return null;
}

/**
 * 查找工作项 ID 所在的集合
 * @param {number} workItemId - 工作项 ID
 * @returns {object} { collectionName, workItem } 或 null
 */
async function findWorkItemCollection(workItemId) {
  const collections = getCollections();
  const results = [];

  // 在所有集合中查找该工作项
  for (const [name, info] of Object.entries(collections)) {
    try {
      const client = new TFSClient(name);
      const workItem = await client.getWorkItem(workItemId);
      if (workItem && workItem.id) {
        results.push({ collectionName: name, workItem });
      }
    } catch (error) {
      // 工作项不存在于该集合，继续查找下一个
      continue;
    }
  }

  return results;
}

/**
 * 交互式选择集合
 * @param {Array} results - 查询结果数组
 * @returns {object} 选中的 { collectionName, workItem }
 */
async function selectCollection(results) {
  return new Promise((resolve, reject) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log(`\n⚠️  工作项在 ${results.length} 个集合中都存在，请选择:\n`);
    results.forEach((r, i) => {
      const title = r.workItem.fields['System.Title'] || '无标题';
      const state = r.workItem.fields['System.State'] || '未知';
      console.log(`  [${i + 1}] 集合: ${r.collectionName}`);
      console.log(`      标题: ${title}`);
      console.log(`      状态: ${state}`);
      console.log();
    });

    const askQuestion = () => {
      rl.question(`请输入选项 (1-${results.length}) 或输入 0 取消: `, (answer) => {
        const choice = parseInt(answer);

        if (choice === 0) {
          rl.close();
          console.log('已取消操作');
          resolve(null);
          return;
        }

        if (choice >= 1 && choice <= results.length) {
          rl.close();
          // 询问是否保存为默认集合
          const selected = results[choice - 1];
          console.log(`\n✓ 已选择集合: ${selected.collectionName}`);
          resolve(selected);
          return;
        }

        console.log('无效选项，请重新输入');
        askQuestion();
      });
    };

    askQuestion();
  });
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    switch (command) {
      case 'collections': {
        const collections = getCollections();
        const defaultCollection = getDefaultCollection();
        console.log('\n可用集合列表:\n');
        Object.entries(collections).forEach(([name, info]) => {
          const isDefault = name === defaultCollection ? ' [默认]' : '';
          console.log(`  ${name}${isDefault}`);
          console.log(`    URL: ${info.url}`);
          console.log(`    描述: ${info.description}`);
          console.log();
        });
        break;
      }

      case 'set-collection': {
        const collectionName = args[1];
        if (!collectionName) {
          console.error('用法: set-collection <collection-name>');
          console.log('可用集合: ' + Object.keys(getCollections()).join(', '));
          process.exit(1);
        }
        setDefaultCollection(collectionName);
        console.log(`默认集合已设置为: ${collectionName}`);
        break;
      }

      case 'my-tasks': {
        const project = args[1] || null;
        let client;

        if (project) {
          client = await getClientForProject(project);
          if (!client) {
            console.error(`项目不存在: ${project}`);
            console.log('使用 "projects" 命令查看可用项目');
            process.exit(1);
          }
        } else {
          client = new TFSClient();
        }

        console.log(`查询分配给我的任务${project ? ` (项目: ${project})` : ''}...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const tasks = await client.getMyTasks(project);
        formatWorkItemTable(tasks);
        break;
      }

      case 'bugs': {
        const project = args[1] || null;
        let client;

        if (project) {
          client = await getClientForProject(project);
          if (!client) {
            console.error(`项目不存在: ${project}`);
            console.log('使用 "projects" 命令查看可用项目');
            process.exit(1);
          }
        } else {
          client = new TFSClient();
        }

        console.log(`查询未关闭的 Bug${project ? ` (项目: ${project})` : ''}...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const bugs = await client.getOpenBugs(project);
        formatWorkItemTable(bugs);
        break;
      }

      case 'resolved': {
        const project = args[1] || null;
        const days = args[2] ? parseInt(args[2]) : 7;
        let client;

        if (project) {
          client = await getClientForProject(project);
          if (!client) {
            console.error(`项目不存在: ${project}`);
            console.log('使用 "projects" 命令查看可用项目');
            process.exit(1);
          }
        } else {
          client = new TFSClient();
        }

        console.log(`查询近 ${days} 天已解决的工作项${project ? ` (项目: ${project})` : ''}...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const items = await client.getRecentResolvedWorkItems(project, days);
        formatWorkItemTable(items);
        break;
      }

      case 'get': {
        const id = parseInt(args[1]);
        const collectionArg = args[2]; // 可选：指定集合

        if (!id) {
          console.error('请提供工作项 ID');
          process.exit(1);
        }

        let targetCollection = collectionArg;
        let results;

        if (targetCollection) {
          // 用户指定了集合，只在指定集合中查找
          console.log(`在集合 "${targetCollection}" 中查找工作项 ${id}...`);
          const client = new TFSClient(targetCollection);
          try {
            const workItem = await client.getWorkItem(id);
            console.log(`✓ 在集合 "${targetCollection}" 中找到工作项\n`);
            console.log(formatWorkItem(workItem));

            // 显示需求分析字段（如果存在）
            const demandAnalysis = workItem.fields['Winning.Demand.Analysis'];
            if (demandAnalysis) {
              console.log(`\n========== 需求分析 ==========`);
              // 简单处理 HTML 标签，提取纯文本内容
              const plainText = demandAnalysis
                .replace(/<br\s*\/?>/gi, '\n')
                .replace(/<\/div>/gi, '\n')
                .replace(/<[^>]+>/g, '')
                .replace(/&nbsp;/g, ' ')
                .replace(/&amp;/g, '&')
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .trim();
              console.log(plainText || '无内容');
            }

            // 显示描述字段
            const description = workItem.fields['System.Description'];
            if (description && description.trim()) {
              console.log(`\n========== 描述 ==========`);
              const plainDesc = description
                .replace(/<br\s*\/?>/gi, '\n')
                .replace(/<\/div>/gi, '\n')
                .replace(/<[^>]+>/g, '')
                .replace(/&nbsp;/g, ' ')
                .trim();
              console.log(plainDesc || '无内容');
            }
          } catch (e) {
            console.error(`工作项 ${id} 在集合 "${targetCollection}" 中未找到`);
            process.exit(1);
          }
          break;
        }

        // 未指定集合，在所有集合中查找
        console.log(`正在所有集合中查找工作项 ${id}...`);
        results = await findWorkItemCollection(id);

        if (results.length === 0) {
          console.error(`工作项 ${id} 在所有集合中都未找到`);
          process.exit(1);
        } else if (results.length === 1) {
          // 只在一个集合中找到，直接使用
          const { collectionName, workItem } = results[0];
          console.log(`✓ 在集合 "${collectionName}" 中找到工作项\n`);
          console.log(formatWorkItem(workItem));

          // 显示需求分析字段（如果存在）
          const demandAnalysis = workItem.fields['Winning.Demand.Analysis'];
          if (demandAnalysis) {
            console.log(`\n========== 需求分析 ==========`);
            const plainText = demandAnalysis
              .replace(/<br\s*\/?>/gi, '\n')
              .replace(/<\/div>/gi, '\n')
              .replace(/<[^>]+>/g, '')
              .replace(/&nbsp;/g, ' ')
              .replace(/&amp;/g, '&')
              .replace(/&lt;/g, '<')
              .replace(/&gt;/g, '>')
              .trim();
            console.log(plainText || '无内容');
          }

          // 显示描述字段
          const description = workItem.fields['System.Description'];
          if (description && description.trim()) {
            console.log(`\n========== 描述 ==========`);
            const plainDesc = description
              .replace(/<br\s*\/?>/gi, '\n')
              .replace(/<\/div>/gi, '\n')
              .replace(/<[^>]+>/g, '')
              .replace(/&nbsp;/g, ' ')
              .trim();
            console.log(plainDesc || '无内容');
          }
        } else {
          // 在多个集合中都找到了，显示所有选项并提示用户如何选择
          console.log(`\n⚠️  工作项 ${id} 在 ${results.length} 个集合中都存在:\n`);
          results.forEach((r, i) => {
            const title = r.workItem.fields['System.Title'] || '无标题';
            const state = r.workItem.fields['System.State'] || '未知';
            console.log(`  [${i + 1}] 集合: ${r.collectionName}`);
            console.log(`      标题: ${title}`);
            console.log(`      状态: ${state}`);
            console.log();
          });
          console.log(`请指定集合查询，用法:`);
          console.log(`  node tools/tfs-query.mjs get ${id} <集合名>`);
          console.log(`\n示例:`);
          results.forEach((r, i) => {
            console.log(`  选项 ${i + 1}: node tools/tfs-query.mjs get ${id} ${r.collectionName}`);
          });
        }
        break;
      }

      case 'get-multi': {
        const ids = args.slice(1).map(s => parseInt(s));
        if (ids.length === 0) {
          console.error('请提供至少一个工作项 ID');
          process.exit(1);
        }

        // 批量获取时使用默认集合
        console.log(`获取工作项: ${ids.join(', ')}...`);
        const client = new TFSClient();
        console.log(`使用集合: ${client.getCollectionName()} (如需其他集合，请先使用 set-collection)`);

        const workItems = await client.getWorkItems(ids);
        formatWorkItemTable(workItems);
        break;
      }

      case 'projects': {
        const client = new TFSClient();
        const projects = client.getProjects();
        const currentCollection = client.getCollectionName();
        console.log(`\n可用项目列表 (集合: ${currentCollection}):\n`);
        Object.entries(projects).forEach(([name, id]) => {
          console.log(`  ${name.padEnd(30)} ${id}`);
        });
        console.log(`\n共 ${Object.keys(projects).length} 个项目\n`);
        break;
      }

      case 'repos': {
        const project = args[1];
        if (!project) {
          console.error('请提供项目名称');
          process.exit(1);
        }

        const client = await getClientForProject(project);
        if (!client) {
          console.error(`项目不存在: ${project}`);
          console.log('使用 "projects" 命令查看可用项目');
          process.exit(1);
        }

        console.log(`获取项目 "${project}" 的 Git 仓库...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const repos = await client.getRepositories(project);
        console.log(`\n找到 ${repos.length} 个仓库:\n`);
        repos.forEach(repo => {
          console.log(`  ${repo.name.padEnd(40)} ${repo.id}`);
          console.log(`    默认分支: ${repo.defaultBranch || '无'}`);
          console.log(`    URL: ${repo.remoteUrl || repo.url}`);
          console.log();
        });
        break;
      }

      case 'commits': {
        const project = args[1];
        const repoId = args[2];
        const top = args[3] ? parseInt(args[3]) : 20;
        const days = args[4] ? parseInt(args[4]) : null;

        if (!project || !repoId) {
          console.error('用法: commits <project> <repoId> [top] [days]');
          process.exit(1);
        }

        const client = await getClientForProject(project);
        if (!client) {
          console.error(`项目不存在: ${project}`);
          console.log('使用 "projects" 命令查看可用项目');
          process.exit(1);
        }

        console.log(`获取最近 ${top} 条提交记录${days ? ` (近 ${days} 天)` : ''}...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const commits = await client.getCommits(repoId, project, top, days);

        console.log(`\n找到 ${commits.length} 条提交:\n`);
        commits.forEach(commit => {
          const shortId = commit.commitId.substring(0, 8);
          const author = commit.author?.displayName || commit.author?.name || '未知';
          const date = new Date(commit.author?.date || commit.commitDate).toLocaleString('zh-CN');
          const comment = commit.comment || '<无评论>';
          const workItemCount = commit.workItems?.length || 0;

          console.log(`${shortId} - ${comment}`);
          console.log(`    作者: ${author} | 日期: ${date} | 关联工作项: ${workItemCount}`);
          console.log();
        });
        break;
      }

      case 'check-commit': {
        const project = args[1];
        const repoId = args[2];
        const commitId = args[3];

        if (!project || !repoId || !commitId) {
          console.error('用法: check-commit <project> <repoId> <commitId>');
          process.exit(1);
        }

        const client = await getClientForProject(project);
        if (!client) {
          console.error(`项目不存在: ${project}`);
          console.log('使用 "projects" 命令查看可用项目');
          process.exit(1);
        }

        console.log(`检查提交 ${commitId.substring(0, 8)} 的工作项关联...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const result = await client.checkCommitWorkItems(repoId, project, commitId);

        console.log(`\n提交: ${result.commitId}`);
        console.log(`关联工作项: ${result.workItemCount} 个`);
        console.log(`状态: ${result.hasWorkItems ? '✓ 已关联' : '✗ 未关联任何工作项'}`);

        if (result.workItemCount > 0) {
          console.log('\n关联的工作项:');
          result.workItems.forEach(wi => {
            console.log(`  - #${wi.id}`);
          });
        }
        console.log();
        break;
      }

      case 'update-state': {
        const id = parseInt(args[1]);
        const newState = args[2];
        const comment = args[3] || null;

        if (!id || !newState) {
          console.error('用法: update-state <workItemId> <newState> [comment]');
          process.exit(1);
        }

        console.log(`更新工作项 ${id} 状态为 "${newState}"...`);
        const client = new TFSClient();
        console.log(`使用集合: ${client.getCollectionName()}`);
        const updated = await client.updateWorkItemState(id, newState, comment);
        console.log(`\n工作项已更新:`);
        console.log(formatWorkItem(updated));
        break;
      }

      case 'create-task': {
        const project = args[1];
        const title = args[2];
        const description = args[3] || '';
        const assignedTo = args[4] || '';

        if (!project || !title) {
          console.error('用法: create-task <project> <title> [description] [assignedTo]');
          process.exit(1);
        }

        const client = await getClientForProject(project);
        if (!client) {
          console.error(`项目不存在: ${project}`);
          console.log('使用 "projects" 命令查看可用项目');
          process.exit(1);
        }

        console.log(`在项目 "${project}" 中创建任务: ${title}...`);
        console.log(`使用集合: ${client.getCollectionName()}`);
        const created = await client.createWorkItem(project, 'Task', {
          title,
          description,
          assignedTo,
          priority: 2
        });

        console.log(`\n任务已创建:`);
        console.log(formatWorkItem(created));
        console.log(`\nURL: ${created._links['html']?.href || ''}`);
        break;
      }

      default:
        showHelp();
    }

  } catch (error) {
    console.error(`错误: ${error.message}`);
    if (error.message.includes('配置文件不存在')) {
      console.log('\n请先配置 TFS 认证信息:');
      console.log('  node tools/setup-config.mjs <your-pat-token>');
    }
    process.exit(1);
  }
}

/**
 * 显示帮助信息
 */
function showHelp() {
  console.log(`
TFS Query Tool - 卫宁健康 WINNING-6.0 团队

用法:
  node tfs-query.mjs <command> [options...]

命令:
  collections                     列出所有可用集合
  set-collection <name>           设置默认集合
  my-tasks [project]              查询分配给我的任务（可选指定项目）
  bugs [project]                  查询未关闭的 Bug（可选指定项目）
  resolved [project] [days]       查询近期已解决的工作项（默认7天）
  get <id> [collection]           获取单个工作项详情（可指定集合）
  get-multi <id1> [id2...]        批量获取工作项（使用默认集合）
  projects                        列出所有可用项目
  repos <project>                 获取项目的 Git 仓库列表
  commits <project> <repoId> [top] [days]  获取最近的提交记录（默认20条，可指定天数）
  check-commit <project> <repoId> <commitId>  检查提交的工作项关联
  update-state <id> <state> [comment]  更新工作项状态
  create-task <project> <title> [description] [assignedTo]  创建任务

示例:
  node tfs-query.mjs collections                      # 列出所有集合
  node tfs-query.mjs set-collection WN_PH-Platform   # 设置默认集合
  node tfs-query.mjs my-tasks                        # 查询我的所有任务
  node tfs-query.mjs my-tasks "WiNEX-PublicHealth"   # 自动切换到 WN_PH-Platform 集合查询
  node tfs-query.mjs bugs "WiNEX-Outpatient"         # 查询门诊项目 Bug
  node tfs-query.mjs get 12345                        # 获取工作项 12345（自动查找集合）
  node tfs-query.mjs get 135557 WINNING-6.0          # 指定集合查询
  node tfs-query.mjs projects                         # 列出所有项目

首次使用:
  请先运行 node tools/setup-config.mjs <your-pat-token> 配置认证信息
`);
}

// 运行
main();
