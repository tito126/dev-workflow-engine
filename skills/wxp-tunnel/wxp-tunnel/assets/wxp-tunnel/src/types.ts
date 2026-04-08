/**
 * wxp-tunnel 类型定义
 */

// ============================================================
// 配置相关
// ============================================================

export interface Config {
  platform: {
    baseUrl: string
    username: string
    password: string
  }
  lockjaw: {
    baseUrl: string
    apiKey: string
  }
  portRange: {
    min: number
    max: number
  }
}

// ============================================================
// Platform API 相关
// ============================================================

export interface User {
  id_user: string | number
  code: string
  name?: string
}

export interface LoginResult {
  user: User
  nameNodeAddrs: string | null
  tenantStatusQueryServers: string | null
}

export interface TenantDTO {
  id_tenant: string
  name: string
  code: string
  online?: boolean
  branchDTOs?: Array<{ id_branch: string }>
}

export interface Tenant {
  id: string
  name: string
  code: string
  online: boolean
  branchId: string
}

export interface LinkDTO {
  id: string
  name: string
  browsetype: string
  sceneformal?: string
  middle_ip: string
  middle_port: number
  middle_realip: string
  middle_realport: number
  opera_ip?: string
  opera_port?: number
  opera_realip?: string
  opera_realport?: number
  url_suffix?: string
  protocol?: string
}

export interface Link {
  id: string
  name: string
  simpleName: string
  accessPoint: string
  targetPoint: string
  localIp: string
  localPort: number
  relIp: string
  relPort: number
  browsetype: string
  protocol: string
  urlSuffix: string
  type: number
  typeLabel: string
  url: string
}

export interface ServiceLink {
  key: string
  name: string
  targetIp?: string
  targetPort: number
  localPort: number | null
  source: 'matched' | 'not_found'
}

// ============================================================
// Lockjaw API 相关
// ============================================================

export interface ChannelParams {
  tenantName: string
  hostId: string
  userName: string
  targetIp: string
  targetPort: number
  channelType?: string
  listenPort?: number
  description?: string
}

export interface Channel {
  channelId: string
  tenantName: string
  hostId: string
  targetIp: string
  targetPort: number
  localPort: number
  status: string
  createTime?: string
}

export interface ApiResponse<T> {
  data: T
  code?: string
  message?: string
}

// ============================================================
// CLI 输出相关
// ============================================================

export interface ServicePortInfo {
  name: string
  targetIp: string
  targetPort: number
  internalAddress: string
  proxyAddress: string | null
  localPort: number | null
  channelId: string | null
  status: string
  needsCreate: boolean
}

export interface ServicePortsResult {
  tenantCode: string
  internalIp: string
  proxyHost: string
  services: Record<string, ServicePortInfo>
}

export interface OpenServiceResult {
  service: string
  status: 'created' | 'already_running' | 'failed'
  internalAddress: string
  proxyAddress?: string
  channelId?: string
  error?: string
}

export interface OpenServicesResult {
  success: boolean
  tenantCode: string
  internalIp: string
  proxyHost: string
  services: OpenServiceResult[]
}

export interface StatusResult {
  lockjawBaseUrl: string
  total: number
  channels: Array<{
    channelId: string
    tenantName: string
    hostId: string
    targetPoint: string
    localPort: number
    status: string
    createdAt?: string
  }>
}
