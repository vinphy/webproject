/**
 * 执行终端命令
 * @param {string} command - 要执行的命令
 * @param {boolean} isBackground - 是否在后台运行
 * @param {boolean} requireUserApproval - 是否需要用户确认
 * @returns {Promise<string>} - 命令执行结果
 */
export const run_terminal_cmd = async (command, isBackground = false, requireUserApproval = true) => {
  try {
    // 这里使用 Node.js 的 child_process 模块执行命令
    const { exec } = require('child_process')
    
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error(`执行命令出错: ${error}`)
          reject(error)
          return
        }
        if (stderr) {
          console.error(`命令错误输出: ${stderr}`)
          reject(new Error(stderr))
          return
        }
        resolve(stdout)
      })
    })
  } catch (error) {
    console.error('执行命令失败:', error)
    throw error
  }
} 