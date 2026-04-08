/**
 * WXP Tunnel CLI
 *
 * 使用 Lockjaw 代理服务管理 TCP 隧道的命令行工具。
 */

import { Command } from 'commander'
import { readFileSync, existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { homedir } from 'node:os'
import * as platform from './platform-client.js'
import * as lockjaw from './lockjaw-client.js'
import type { Config, User, Tenant, Link, LinkDTO, ServicePortsResult, ServicePortInfo, OpenServicesResult, StatusResult } from './types.js'

/**
 * 获取配置文件目录
 */
function getConfigDir(): string {
  return resolve(homedir(), '.cache', 'wxp-tunnel')
}

/**
 * 获取配置文件路径
 */
function getConfigPath(): string {
  return resolve(getConfigDir(), 'config.json')
}

/**
 * 从 Lockjaw baseUrl 中提取主机 IP
 */
function getProxyHost(baseUrl: string): string {
  try {
    const url = new URL(baseUrl)
    return url.hostname
  } catch {
    return '127.0.0.1'
  }
}

/**
 * 加载配置文件
 */
function loadConfig(): Config {
  const configDir = getConfigDir()
  const configPath = getConfigPath()

  // 如果配置目录不存在，创建并生成模板
  if (!existsSync(configDir)) {
    mkdirSync(configDir, { recursive: true })
  }

  if (!existsSync(configPath)) {
    // 创建默认配置模板
    const defaultConfig: Config = {
      platform: {
        baseUrl: "https://wxpcpp.winning.com.cn:2443/",
        username: "your_username",
        password: "your_password"
      },
      lockjaw: {
        baseUrl: "http://localhost:8765",
        apiKey: "dev-test-key"
      },
      portRange: {
        min: 8000,
        max: 9000
      }
    }
    writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2))
    console.error(`已创建配置文件模板: ${configPath}`)
    console.error(`请编辑配置文件并填入正确的凭据后重试。`)
    process.exit(1)
  }

  const raw = readFileSync(configPath, 'utf-8')
  return JSON.parse(raw) as Config
}

/**
 * 登录平台并获取用户信息
 */
async function ensureLogin(config: Config): Promise<User> {
  const result = await platform.login(
    config.platform.baseUrl,
    config.platform.username,
    config.platform.password
  )
  return result.user
}

/**
 * 获取租户列表
 */
async function getTenantList(config: Config, user: User): Promise<Tenant[]> {
  const tenantDTOs = await platform.getTenants(
    config.platform.baseUrl,
    user.id_user
  )
  return tenantDTOs.map((item): Tenant => ({
    id: item.id_tenant,
    name: item.name,
    code: item.code,
    online: item.online || false,
    branchId: item.branchDTOs?.[0]?.id_branch || ''
  }))
}

/**
 * 格式化连接列表
 */
function formatLinks(links: LinkDTO[]): Link[] {
  return links.map((item): Link => {
    const row: Link = {
      id: item.id,
      name: item.name,
      simpleName: item.name.substring(0, item.name.indexOf('(转发')) || item.name,
      accessPoint: `${item.middle_ip}:${item.middle_port}`,
      targetPoint: `${item.middle_realip}:${item.middle_realport}`,
      localIp: item.middle_ip,
      localPort: item.middle_port,
      relIp: item.middle_realip,
      relPort: item.middle_realport,
      browsetype: item.browsetype,
      protocol: item.protocol?.includes('https') ? 'https' : 'http',
      urlSuffix: item.url_suffix || '',
      type: 3,
      typeLabel: '其他',
      url: ''
    }
    const { type, url } = platform.getActualURL(row)
    row.type = type
    row.typeLabel = platform.TYPE_LABELS[type] || '其他'
    row.url = url
    return row
  }).sort((a, b) => a.type - b.type)
}

interface InternalService {
  key: string
  name: string
  targetPort: number
  targetIp?: string
  source: string
}

/**
 * 获取服务端口信息
 */
async function getServicePorts(config: Config, tenantCode: string): Promise<ServicePortsResult> {
  const user = await ensureLogin(config)
  const tenants = await getTenantList(config, user)
  const tenant = tenants.find((t) => t.code === tenantCode)
  if (!tenant) {
    throw new Error(`未找到租户: ${tenantCode}`)
  }

  const links = await platform.getTenantLinks(
    config.platform.baseUrl,
    user.code,
    tenant.branchId
  )
  const formattedLinks = formatLinks(links)

  // 获取已创建的隧道
  const channels = await lockjaw.getChannels(
    config.lockjaw.baseUrl,
    config.lockjaw.apiKey
  )

  // 获取代理服务器主机地址
  const proxyHost = getProxyHost(config.lockjaw.baseUrl)

  // 找到运维平台的内网IP
  const opsLink = formattedLinks.find((l) => l.type === 0)
  if (!opsLink) {
    throw new Error(`未找到运维平台连接: ${tenantCode}`)
  }
  const internalIp = opsLink.relIp

  // 运维平台：强制使用 http 8089 端口
  // 优先查找 8089 端口的连接，如果没有则使用 8089 作为目标端口
  const ops8089Link = formattedLinks.find(
    (l) => l.relIp === internalIp && String(l.relPort) === '8089'
  )
  const opsService: InternalService = {
    key: 'ops',
    name: '运维平台',
    targetPort: ops8089Link ? ops8089Link.relPort : 8089,
    targetIp: internalIp,
    source: ops8089Link ? 'matched' : 'allocated'
  }

  // Prometheus：只使用名称匹配，不依赖端口
  const promService = platform.findServiceLink(
    formattedLinks,
    internalIp,
    'prometheus',
    ['prometheus', 'prom'],
    [9090]
  )
  promService.targetIp = internalIp

  // InfluxDB：使用端口和名称匹配
  const influxService = platform.findServiceLink(
    formattedLinks,
    internalIp,
    'influxdb',
    ['influx'],
    [8086]
  )
  influxService.targetIp = internalIp

  const services: InternalService[] = [opsService, promService, influxService]

  const result: ServicePortsResult = {
    tenantCode,
    internalIp,
    proxyHost,
    services: {}
  }

  for (const svc of services) {
    const targetPort = svc.targetPort
    const targetIp = svc.targetIp!

    // 检查是否已有隧道
    const hostId = `${targetIp}-${targetPort}`
    const existingChannel = channels.find((ch) => ch.hostId === hostId)

    result.services[svc.key] = {
      name: svc.name,
      targetIp,
      targetPort,
      internalAddress: `${targetIp}:${targetPort}`,
      proxyAddress: existingChannel ? `${proxyHost}:${existingChannel.localPort}` : null,
      localPort: existingChannel?.localPort || null,
      channelId: existingChannel?.channelId || null,
      status: existingChannel?.status || 'NONE',
      needsCreate: !existingChannel
    }
  }

  return result
}

// ============================================================
// CLI 程序
// ============================================================

const program = new Command()

program
  .name('wxp-tunnel')
  .description('WXP Tunnel - 使用 Lockjaw 代理服务管理 TCP 隧道')
  .version('2.0.0')

/**
 * 命令: tenants
 * 列出所有可用租户
 */
program
  .command('tenants')
  .description('列出所有可用租户')
  .argument('[keyword]', '可选的筛选关键字，匹配租户名称或编码')
  .option('-k, --keyword <keyword>', '可选的筛选关键字，匹配租户名称或编码（与位置参数等效）')
  .action(async (keyword: string | undefined, options: { keyword?: string }) => {
    try {
      const config = loadConfig()
      const user = await ensureLogin(config)
      let tenants = await getTenantList(config, user)

      // 支持位置参数和 -k 选项两种方式
      const filterKeyword = keyword || options.keyword
      if (filterKeyword) {
        const kw = filterKeyword.toLowerCase()
        tenants = tenants.filter(
          (t) => t.name.toLowerCase().includes(kw) || t.code.toLowerCase().includes(kw)
        )
      }

      console.log(JSON.stringify(tenants, null, 2))
    } catch (err) {
      const error = err as Error & { statusCode?: number; getUserMessage?: () => string }
      if (error.statusCode && error.getUserMessage) {
        console.error(`错误: ${error.getUserMessage()}`)
      } else {
        console.error(`错误: ${error.message}`)
      }
      process.exit(1)
    }
  })

/**
 * 命令: links
 * 列出指定租户的所有可用连接
 */
program
  .command('links')
  .description('列出指定租户的所有可用连接')
  .argument('<tenantCode>', '租户编码')
  .action(async (tenantCode: string) => {
    try {
      const config = loadConfig()
      const user = await ensureLogin(config)
      const tenants = await getTenantList(config, user)
      const tenant = tenants.find((t) => t.code === tenantCode)
      if (!tenant) {
        throw new Error(`未找到租户: ${tenantCode}`)
      }

      const links = await platform.getTenantLinks(
        config.platform.baseUrl,
        user.code,
        tenant.branchId
      )
      const formattedLinks = formatLinks(links)

      console.log(JSON.stringify(formattedLinks, null, 2))
    } catch (err) {
      const error = err as Error & { statusCode?: number; getUserMessage?: () => string }
      if (error.statusCode && error.getUserMessage) {
        console.error(`错误: ${error.getUserMessage()}`)
      } else {
        console.error(`错误: ${error.message}`)
      }
      process.exit(1)
    }
  })

/**
 * 命令: service-ports
 * 获取租户的三个监控服务端口映射
 */
program
  .command('service-ports')
  .description('获取租户的三个监控服务端口映射（运维平台、Prometheus、InfluxDB）')
  .argument('<tenantCode>', '租户编码')
  .action(async (tenantCode: string) => {
    try {
      const config = loadConfig()
      const result = await getServicePorts(config, tenantCode)
      console.log(JSON.stringify(result, null, 2))
    } catch (err) {
      const error = err as Error & { statusCode?: number; getUserMessage?: () => string }
      if (error.statusCode && error.getUserMessage) {
        console.error(`错误: ${error.getUserMessage()}`)
      } else {
        console.error(`错误: ${error.message}`)
      }
      process.exit(1)
    }
  })

/**
 * 命令: open-services
 * 自动打开租户的三个监控服务隧道
 */
program
  .command('open-services')
  .description('自动打开租户的三个监控服务隧道（运维平台、Prometheus、InfluxDB）')
  .argument('<tenantCode>', '租户编码')
  .action(async (tenantCode: string) => {
    try {
      const config = loadConfig()
      const portInfo = await getServicePorts(config, tenantCode)
      const user = await ensureLogin(config)

      const results: OpenServicesResult['services'] = []

      for (const [serviceKey, serviceInfo] of Object.entries(portInfo.services)) {
        try {
          if (serviceInfo.status === 'RUNNING') {
            results.push({
              service: serviceInfo.name,
              status: 'already_running',
              internalAddress: `${serviceInfo.targetIp}:${serviceInfo.targetPort}`,
              proxyAddress: `${portInfo.proxyHost}:${serviceInfo.localPort}`,
              channelId: serviceInfo.channelId || undefined
            })
            continue
          }

          const hostId = `${serviceInfo.targetIp}-${serviceInfo.targetPort}`
          const channel = await lockjaw.createChannel(
            config.lockjaw.baseUrl,
            config.lockjaw.apiKey,
            {
              tenantName: tenantCode,
              hostId,
              userName: user.code,
              targetIp: serviceInfo.targetIp,
              targetPort: serviceInfo.targetPort,
              channelType: 'TCP',
              description: `WXP Tunnel - ${serviceInfo.name} (${tenantCode})`
            }
          )

          results.push({
            service: serviceInfo.name,
            status: 'created',
            internalAddress: `${serviceInfo.targetIp}:${serviceInfo.targetPort}`,
            proxyAddress: `${portInfo.proxyHost}:${channel.localPort}`,
            channelId: channel.channelId
          })
        } catch (err) {
          const error = err as Error
          results.push({
            service: serviceInfo.name,
            status: 'failed',
            internalAddress: `${serviceInfo.targetIp}:${serviceInfo.targetPort}`,
            error: error.message
          })
        }
      }

      console.log(JSON.stringify({
        success: true,
        tenantCode: portInfo.tenantCode,
        internalIp: portInfo.internalIp,
        proxyHost: portInfo.proxyHost,
        services: results
      } as OpenServicesResult, null, 2))
    } catch (err) {
      const error = err as Error & { statusCode?: number; getUserMessage?: () => string }
      if (error.statusCode && error.getUserMessage) {
        console.error(`错误: ${error.getUserMessage()}`)
      } else {
        console.error(`错误: ${error.message}`)
      }
      process.exit(1)
    }
  })

/**
 * 命令: close
 * 关闭指定隧道
 */
program
  .command('close')
  .description('关闭指定的隧道')
  .argument('<channelId>', '通道 ID')
  .action(async (channelId: string) => {
    try {
      const config = loadConfig()
      await lockjaw.deleteChannel(
        config.lockjaw.baseUrl,
        config.lockjaw.apiKey,
        channelId
      )
      console.log(JSON.stringify({
        success: true,
        message: `通道 ${channelId} 已删除`
      }, null, 2))
    } catch (err) {
      const error = err as Error & { statusCode?: number; getUserMessage?: () => string }
      if (error.statusCode && error.getUserMessage) {
        console.error(`错误: ${error.getUserMessage()}`)
      } else {
        console.error(`错误: ${error.message}`)
      }
      process.exit(1)
    }
  })

/**
 * 命令: status
 * 查看当前所有活跃隧道
 */
program
  .command('status')
  .description('查看当前所有活跃隧道')
  .action(async () => {
    try {
      const config = loadConfig()
      const channels = await lockjaw.getChannels(
        config.lockjaw.baseUrl,
        config.lockjaw.apiKey
      )

      const result: StatusResult = {
        lockjawBaseUrl: config.lockjaw.baseUrl,
        total: channels.length,
        channels: channels.map((ch) => ({
          channelId: ch.channelId,
          tenantName: ch.tenantName,
          hostId: ch.hostId,
          targetPoint: `${ch.targetIp}:${ch.targetPort}`,
          localPort: ch.localPort,
          status: ch.status,
          createdAt: ch.createTime
        }))
      }

      console.log(JSON.stringify(result, null, 2))
    } catch (err) {
      const error = err as Error & { statusCode?: number; getUserMessage?: () => string }
      if (error.statusCode && error.getUserMessage) {
        console.error(`错误: ${error.getUserMessage()}`)
      } else {
        console.error(`错误: ${error.message}`)
      }
      process.exit(1)
    }
  })

program.parse()
