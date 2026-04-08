/**
 * Platform API Client
 *
 * 封装与云平台后端的 HTTP 交互：登录、获取租户列表、获取连接列表。
 * 移植自原有的 api-client.js。
 */

import type { User, LoginResult, TenantDTO, LinkDTO, Link, ServiceLink } from './types.js'

interface RequestOptions {
  method?: string
  body?: string
  timeout?: number
  headers?: Record<string, string>
}

/**
 * 统一请求封装
 */
async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  // 允许自签名证书
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'

  const fetchOptions: RequestInit & { signal: AbortSignal } = {
    ...options,
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    signal: AbortSignal.timeout(options.timeout || 15000)
  }

  const resp = await fetch(url, fetchOptions)
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}: ${resp.statusText} - ${url}`)
  }
  const contentType = resp.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return resp.json() as Promise<T>
  }
  return resp.text() as Promise<T>
}

/**
 * 拼接 query 参数
 */
function withParams(url: string, params: Record<string, string | number | undefined>): string {
  if (!params) return url
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined)
      .map(([k, v]) => [k, String(v)])
  ).toString()
  return qs ? `${url}${url.includes('?') ? '&' : '?'}${qs}` : url
}

// ============================================================
// API 方法
// ============================================================

interface LoginResponse {
  data: {
    loginResult: string | number
    user: User
    cdpParamgroupDTOs?: Array<{
      cdpParamDTOs?: Array<{ code: string; value: string }>
    }>
  }
}

/**
 * 登录平台
 */
export async function login(baseUrl: string, username: string, password: string): Promise<LoginResult> {
  const data = await request<LoginResponse>(`${baseUrl}api/v1/wxpclient/login`, {
    method: 'POST',
    body: JSON.stringify({ username, password, encryptType: 'cxp' })
  })

  if (!data || !data.data) {
    throw new Error('登录失败：未获取到响应数据')
  }

  const loginResult = data.data.loginResult
  if (loginResult !== 'LOGIN_SUCCESS' && loginResult !== 0 && loginResult !== 'NO_AVAILABLE_TENANT_ERROR') {
    throw new Error(`登录失败：${loginResult}`)
  }

  let nameNodeAddrs: string | null = null
  let tenantStatusQueryServers: string | null = null

  if (data.data.cdpParamgroupDTOs && data.data.cdpParamgroupDTOs[0]) {
    const params = data.data.cdpParamgroupDTOs[0].cdpParamDTOs || []

    const nameNodeParam = params.find(
      (item) => item.code === 'XapDataRelaySystemNameNodeAddr'
    )
    if (nameNodeParam) {
      nameNodeAddrs = nameNodeParam.value
    }

    const statusQueryParam = params.find(
      (item) => item.code === 'DataRelaySystemTenantStatusQueryServers'
    )
    if (statusQueryParam) {
      tenantStatusQueryServers = statusQueryParam.value
    }
  }

  return {
    user: data.data.user,
    nameNodeAddrs,
    tenantStatusQueryServers
  }
}

interface TenantsResponse {
  data?: TenantDTO[]
}

/**
 * 获取租户列表
 */
export async function getTenants(baseUrl: string, idUser: string | number): Promise<TenantDTO[]> {
  const url = withParams(`${baseUrl}api/v2/wxpclient/getUserTenants`, { idUser })
  const data = await request<TenantsResponse>(url, { method: 'GET' })
  return data?.data || []
}

/**
 * 获取租户状态（在线/离线）
 */
export async function getTenantStatus(server: string): Promise<{ agentnodes: unknown[] }> {
  const url = `http://${server}/proxy/select/listCacheTenants?pageSize=-1&pageIndex=-1`
  return request(url, { method: 'GET', timeout: 5000 })
}

/**
 * 获取远程系统时间
 */
export async function getSysDate(server: string): Promise<{ sysdate: number }> {
  const url = `http://${server}/name/sysdate`
  return request(url, { method: 'GET', timeout: 5000 })
}

interface LinksResponse {
  data?: LinkDTO[]
}

/**
 * 获取指定租户的所有可用连接列表
 */
export async function getTenantLinks(
  baseUrl: string,
  usercode: string,
  idBranch: string | number
): Promise<LinkDTO[]> {
  const url = withParams(`${baseUrl}suit/getByUserAndBranch`, {
    usercode,
    idBranch
  })
  const data = await request<LinksResponse>(url, { method: 'GET' })
  return data?.data || []
}

interface LinkRow {
  browsetype: string
  operaPort?: number
  localPort?: number
  protocol: string
  accessPoint: string
  urlSuffix: string
  simpleName?: string
}

/**
 * 计算连接的实际访问 URL 和类型
 */
export function getActualURL(row: LinkRow): { type: number; url: string } {
  let type = 3
  let url: string

  if (row.browsetype === 'yumbrowse' || row.operaPort === row.localPort) {
    // 运维平台
    type = 0
    url = `${row.protocol}://${row.accessPoint}/cluster/action/index/welcome`
  } else if (row.browsetype === 'deliverbrowse') {
    // 交付平台
    type = 1
    url = `${row.protocol}://${row.accessPoint}/deliver/#/home`
  } else if (row.urlSuffix) {
    // 有自定义后缀
    const suffix = row.urlSuffix.startsWith('/') ? row.urlSuffix : `/${row.urlSuffix}`
    url = `${row.protocol}://${row.accessPoint}${suffix}`
  } else if (isPortal(row)) {
    // 门户
    type = 2
    url = `${row.protocol}://${row.accessPoint}/portal/#/login`
  } else {
    url = `${row.protocol}://${row.accessPoint}`
  }

  return { type, url }
}

/**
 * 判断是否为门户连接
 */
function isPortal(row: LinkRow): boolean {
  if (row.urlSuffix) {
    return row.urlSuffix.indexOf('portal') !== -1
  }
  return (row.simpleName || '').toLowerCase().indexOf('portal') !== -1
}

/** 类型标签 */
export const TYPE_LABELS: Record<number, string> = { 0: '运维平台', 1: '交付平台', 2: '门户Portal', 3: '其他' }

/**
 * 智能查找服务连接
 */
export function findServiceLink(
  links: Link[],
  internalIp: string,
  serviceKey: string,
  keywords: string[],
  commonPorts: number[]
): ServiceLink {
  const serviceName = serviceKey.charAt(0).toUpperCase() + serviceKey.slice(1)

  // 优先级1: 同IP + 常见端口匹配
  for (const port of commonPorts) {
    const matched = links.find((l) => l.relIp === internalIp && String(l.relPort) === String(port))
    if (matched) {
      return { key: serviceKey, name: serviceName, targetPort: matched.relPort, localPort: matched.localPort, source: 'matched' }
    }
  }

  // 优先级2: 同IP + 名称关键字匹配
  for (const keyword of keywords) {
    const matched = links.find((l) =>
      l.relIp === internalIp &&
      (l.simpleName?.toLowerCase().includes(keyword) || l.name?.toLowerCase().includes(keyword))
    )
    if (matched) {
      return { key: serviceKey, name: serviceName, targetPort: matched.relPort, localPort: matched.localPort, source: 'matched' }
    }
  }

  // 优先级3: 任意IP + 常见端口匹配
  for (const port of commonPorts) {
    const matched = links.find((l) => String(l.relPort) === String(port))
    if (matched) {
      return { key: serviceKey, name: serviceName, targetPort: matched.relPort, localPort: matched.localPort, source: 'matched' }
    }
  }

  // 优先级4: 任意IP + 名称关键字匹配
  for (const keyword of keywords) {
    const matched = links.find((l) =>
      (l.simpleName?.toLowerCase().includes(keyword) || l.name?.toLowerCase().includes(keyword))
    )
    if (matched) {
      return { key: serviceKey, name: serviceName, targetPort: matched.relPort, localPort: matched.localPort, source: 'matched' }
    }
  }

  // 未找到：使用默认端口
  const defaultPorts: Record<string, number> = {
    prometheus: 9090,
    influxdb: 8086
  }
  const defaultPort = commonPorts.length > 0 ? commonPorts[0] : (defaultPorts[serviceKey] || 8080)
  return { key: serviceKey, name: serviceName, targetPort: defaultPort, localPort: null, source: 'not_found' }
}
