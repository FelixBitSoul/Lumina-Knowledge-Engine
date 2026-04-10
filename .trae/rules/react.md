# React 开发规范

## 1. 组件开发

### 1.1 组件结构
- **函数组件优先**：使用函数组件配合Hooks，替代class组件
- **组件拆分原则**：单一职责，一个组件只做一件事
- **文件命名**：使用PascalCase命名组件文件，如 `UserCard.tsx`
- **目录结构**：按功能模块化组织，相关文件放在同一目录

### 1.2 代码风格
- **函数声明**：使用函数声明定义组件，箭头函数定义事件处理函数
- **Props验证**：使用TypeScript确保类型安全
- **早期返回**：使用早期返回模式减少嵌套，提高代码可读性
- **避免嵌套三元表达式**：复杂条件使用早期返回，简单条件使用三元表达式

### 1.3 状态管理
- **状态定位**：状态应尽可能靠近使用它的组件
- **简单状态**：使用 `useState` 管理简单状态
- **复杂状态**：考虑使用Context或Redux管理复杂状态
- **避免过度使用全局状态**：优先使用局部状态

## 2. Hooks 使用

### 2.1 基本规则
- **只在顶层调用**：Hooks只能在组件顶层调用，不能在条件语句、循环或嵌套函数中调用
- **只在React函数中调用**：Hooks只能在React函数组件或自定义Hooks中调用
- **依赖数组**：正确设置useEffect、useCallback等的依赖数组

### 2.2 性能优化
- **避免过度使用useMemo和useCallback**：React 18+的编译器会自动优化，手动添加可能会适得其反
- **合理使用useCallback**：对于传递给子组件的回调函数，使用useCallback避免不必要的重渲染
- **合理使用useMemo**：对于复杂计算结果，使用useMemo缓存

### 2.3 自定义Hooks
- **命名规范**：自定义Hooks应以 `use` 开头
- **逻辑复用**：将可复用的逻辑提取到自定义Hooks中
- **类型安全**：为自定义Hooks添加适当的TypeScript类型

## 3. 项目结构

### 3.1 目录组织
- **功能模块化**：按功能组织目录，而非按文件类型
- **共享组件**：将可复用组件放在 `shared` 或 `components` 目录
- **特性模块**：将业务功能放在 `features` 目录
- **工具函数**：将通用工具函数放在 `utils` 目录
- **API服务**：将API调用放在 `services` 目录

### 3.2 文件命名
- **组件文件**：PascalCase，如 `UserCard.tsx`
- **非组件文件**：kebab-case，如 `use-fetch.ts`
- **测试文件**：与被测试文件同名，添加 `.test` 或 `.spec` 后缀

## 4. 代码质量

### 4.1 ESLint与Prettier
- **ESLint配置**：使用Airbnb风格指南，配合ESLint React插件
- **Prettier配置**：统一代码格式化规则
- **Git Hooks**：使用pre-commit钩子在提交前运行lint和格式化

### 4.2 测试
- **测试类型**：单元测试、集成测试、端到端测试
- **测试工具**：Jest + React Testing Library
- **测试覆盖率**：保持足够的测试覆盖率

### 4.3 性能优化
- **Server Components**：在Next.js中优先使用Server Components
- **Suspense**：使用Suspense处理数据加载
- **代码分割**：使用动态导入实现代码分割
- **图片优化**：使用适当的图片格式和大小

## 5. 最佳实践

### 5.1 数据获取
- **Server Components**：在Server Components中直接获取数据
- **Client Components**：使用SWR或React Query处理客户端数据获取
- **避免useEffect数据获取**：在现代React中，优先使用更高级的数据获取方案

### 5.2 错误处理
- **Error Boundaries**：使用Error Boundaries捕获组件错误
- **Try-Catch**：在异步操作中使用try-catch处理错误
- **错误状态**：为用户提供清晰的错误反馈

### 5.3 可访问性
- **ARIA属性**：为交互式元素添加适当的ARIA属性
- **键盘导航**：确保所有功能可通过键盘访问
- **语义化HTML**：使用语义化的HTML元素

### 5.4 国际化
- **i18n**：使用国际化库处理多语言支持
- **文本提取**：将所有用户可见的文本提取到翻译文件

## 6. 版本控制

### 6.1 Git工作流
- **分支策略**：使用Feature-branch工作流
- **提交信息**：遵循Conventional Commits规范
- **代码审查**：所有代码变更都应经过代码审查

### 6.2 部署
- **CI/CD**：使用持续集成和持续部署
- **环境变量**：使用.env文件管理环境变量
- **构建优化**：优化生产构建

## 7. 与现代栈集成

### 7.1 Next.js
- **App Router**：使用Next.js App Router和Server Components
- **Route Groups**：使用Route Groups组织路由
- **Server Actions**：使用Server Actions处理表单提交

### 7.2 TypeScript
- **严格模式**：启用TypeScript严格模式
- **类型定义**：为所有组件和函数添加类型定义
- **接口设计**：合理设计TypeScript接口

### 7.3 状态管理
- **Zustand**：对于简单状态管理，考虑使用Zustand
- **Redux Toolkit**：对于复杂状态管理，使用Redux Toolkit
- **Jotai**：对于原子状态管理，考虑使用Jotai

## 8. 反模式

### 8.1 组件相关
- **过度渲染**：避免不必要的组件渲染
- **大组件**：避免创建过于复杂的组件
- **props drilling**：避免多层级传递props
- **硬编码**：避免在组件中硬编码值

### 8.2 Hooks相关
- **在条件中使用Hooks**：违反Hooks规则
- **过度使用useEffect**：将useEffect用于不适合的场景
- **依赖数组错误**：错误设置依赖数组导致无限循环

### 8.3 性能相关
- **同步渲染大列表**：应使用虚拟滚动
- **未优化的图片**：应使用适当的图片格式和大小
- **未使用的依赖**：应移除未使用的依赖

## 9. 代码示例

### 9.1 组件示例

```tsx
// 推荐的组件结构
function UserCard({ user, onEdit }: UserCardProps) {
  if (!user) {
    return <EmptyState message="User not found" />;
  }

  const handleEdit = () => {
    onEdit(user.id);
  };

  return (
    <div className="user-card">
      <div className="user-avatar">
        <img src={user.avatar} alt={user.name} />
      </div>
      <div className="user-info">
        <h3>{user.name}</h3>
        <p>{user.email}</p>
      </div>
      <button onClick={handleEdit}>
        Edit
      </button>
    </div>
  );
}
```

### 9.2 自定义Hook示例

```tsx
// 推荐的自定义Hook
function useData<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        const result = await response.json();
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [url]);

  return { data, loading, error };
}
```

## 10. 总结

React开发规范旨在帮助开发者构建高质量、可维护的React应用。随着React生态系统的不断发展，这些规范也应随之更新。开发者应关注React官方文档和社区最佳实践，不断提升自己的开发技能。