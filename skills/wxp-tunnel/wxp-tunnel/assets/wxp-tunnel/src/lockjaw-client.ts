/**
 * Lockjaw API Client
 *
 * 封装 Lockjaw 代理服务的 HTTP API 接口。
 * 参考: references/API.md
 */

import type { Channel, ChannelParams, ApiResponse } from './types.js'

interface RequestOptions {
  method?: string
  body?: string
  timeout?: number
  headers?: Record<string, string>
}

/**
 * 统一请求封装
 */
async function request<T>(
  baseUrl: string,
  apiKey: string,
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${baseUrl}${path}`
  const fetchOptions: RequestInit & { signal: AbortSignal } = {
    ...options,
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
      ...options.headers
    },
    signal: AbortSignal.timeout(options.timeout || 15000)
  }

  const resp = await fetch(url, fetchOptions)

  // 处理错误响应
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({ message: resp.statusText })) as { message?: string; code?: string }
    throw new LockjawError(resp.status, errorData.message || errorData.code || resp.statusText)
  }

  return resp.json() as Promise<T>
}

/**
 * Lockjaw API 错误类
 */
export class LockjawError extends Error {
  statusCode: number

  constructor(statusCode: number, message: string) {
    super(message)
    this.statusCode = statusCode
    this.name = 'LockjawError'
  }

  /**
   * 获取用户友好的错误消息
   */
  getUserMessage(): string {
    switch (this.statusCode) {
      case 401:
        return 'API Key 无效，请检查配置文件中的 lockjaw.apiKey'
      case 403:
        return 'IP 地址不在白名单内，请联系管理员添加'
      case 409:
        return '资源冲突（通道已存在）'
      default:
        return this.message
    }
  }
}

/**
 * 创建隧道
 */
export async function createChannel(
  baseUrl: string,
  apiKey: string,
  params: ChannelParams
): Promise<Channel> {
  const { tenantName, hostId, userName, targetIp, targetPort, channelType = 'TCP', listenPort, description } = params

  const data = await request<ApiResponse<Channel>>(baseUrl, apiKey, '/api/v1/lockjaw/channels', {
    method: 'POST',
    body: JSON.stringify({
      tenantName,
      hostId,
      userName,
      targetIp,
      targetPort,
      channelType,
      listenPort,
      description
    })
  })

  return data.data
}

/**
 * 查询隧道列表
 */
export async function getChannels(baseUrl: string, apiKey: string): Promise<Channel[]> {
  const data = await request<ApiResponse<Channel[]>>(baseUrl, apiKey, '/api/v1/lockjaw/channels', {
    method: 'GET'
  })
  return data.data || []
}

/**
 * 查询指定隧道
 */
export async function getChannel(
  baseUrl: string,
  apiKey: string,
  channelId: string
): Promise<Channel> {
  const data = await request<ApiResponse<Channel>>(baseUrl, apiKey, `/api/v1/lockjaw/channels/${channelId}`, {
    method: 'GET'
  })
  return data.data
}

/**
 * 删除隧道
 */
export async function deleteChannel(
  baseUrl: string,
  apiKey: string,
  channelId: string
): Promise<boolean> {
  await request(baseUrl, apiKey, `/api/v1/lockjaw/channels/${channelId}`, {
    method: 'DELETE'
  })
  return true
}

/**
 * 健康检查
 */
export async function healthCheck(baseUrl: string): Promise<Record<string, unknown>> {
  const resp = await fetch(`${baseUrl}/actuator/health`, {
    signal: AbortSignal.timeout(5000)
  })
  return resp.json() as Promise<Record<string, unknown>>
}
