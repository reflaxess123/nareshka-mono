import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextSize } from '@/shared/components/Text';
import {
  useChangeUserRole,
  useDeleteUser,
  useUsers,
} from '@/shared/hooks/useAdminAPI';
import { Crown, Trash2, User, UserCheck, UserX } from 'lucide-react';
import { useState } from 'react';
import styles from './UserManagement.module.scss';

export const UserManagement = () => {
  const { data: users = [], isLoading: loading, error, refetch } = useUsers();
  const changeUserRoleMutation = useChangeUserRole();
  const deleteUserMutation = useDeleteUser();
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const changeUserRole = async (userId: number, newRole: 'USER' | 'ADMIN') => {
    try {
      setActionLoading(userId);
      await changeUserRoleMutation.mutateAsync({ userId, newRole });
    } catch (error) {
      console.error('Ошибка изменения роли:', error);
      alert('Не удалось изменить роль пользователя');
    } finally {
      setActionLoading(null);
    }
  };

  const deleteUser = async (userId: number, userEmail: string) => {
    if (
      !confirm(`Удалить пользователя ${userEmail}? Это действие необратимо.`)
    ) {
      return;
    }

    try {
      setActionLoading(userId);
      await deleteUserMutation.mutateAsync(userId);
    } catch (error) {
      console.error('Ошибка удаления пользователя:', error);
      alert('Не удалось удалить пользователя');
    } finally {
      setActionLoading(null);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return <Crown size={16} className={styles.adminIcon} />;
      case 'USER':
        return <UserCheck size={16} className={styles.userIcon} />;
      case 'GUEST':
        return <User size={16} className={styles.guestIcon} />;
      default:
        return <User size={16} />;
    }
  };

  const getRoleText = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return 'Администратор';
      case 'USER':
        return 'Пользователь';
      case 'GUEST':
        return 'Гость';
      default:
        return role;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <PageWrapper>
        <div className={styles.userManagement}>
          <div className={styles.loading}>
            <Text text="⏳ Загрузка пользователей..." size={TextSize.LG} />
          </div>
        </div>
      </PageWrapper>
    );
  }

  if (error) {
    return (
      <PageWrapper>
        <div className={styles.userManagement}>
          <div className={styles.error}>
            <Text text="❌ Ошибка загрузки" size={TextSize.LG} />
            <Text
              text={
                error instanceof Error
                  ? error.message
                  : 'Не удалось загрузить список пользователей'
              }
              size={TextSize.MD}
            />
            <Button onClick={() => refetch()} variant={ButtonVariant.PRIMARY}>
              Попробовать снова
            </Button>
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <div className={styles.userManagement}>
        <div className={styles.header}>
          <Text text="👥 Управление пользователями" size={TextSize.LG} />
          <Text
            text={`Всего пользователей: ${users.length}`}
            size={TextSize.MD}
            className={styles.subtitle}
          />
        </div>

        <div className={styles.actions}>
          <Button
            onClick={() => refetch()}
            variant={ButtonVariant.SECONDARY}
            disabled={loading}
          >
            🔄 Обновить
          </Button>
        </div>

        <div className={styles.usersList}>
          {users.length === 0 ? (
            <div className={styles.empty}>
              <Text text="Пользователи не найдены" size={TextSize.LG} />
            </div>
          ) : (
            <div className={styles.usersGrid}>
              {users.map((user) => (
                <div key={user.id} className={styles.userCard}>
                  <div className={styles.userInfo}>
                    <div className={styles.userHeader}>
                      <div className={styles.roleContainer}>
                        {getRoleIcon(user.role)}
                        <span className={styles.roleText}>
                          {getRoleText(user.role)}
                        </span>
                      </div>
                      <span className={styles.userId}>ID: {user.id}</span>
                    </div>

                    <div className={styles.userEmail}>
                      <Text text={user.email} size={TextSize.MD} />
                    </div>

                    <div className={styles.userDates}>
                      <div className={styles.dateItem}>
                        <span className={styles.dateLabel}>Регистрация:</span>
                        <span className={styles.dateValue}>
                          {formatDate(user.createdAt)}
                        </span>
                      </div>
                      {user.lastActiveAt && (
                        <div className={styles.dateItem}>
                          <span className={styles.dateLabel}>
                            Последняя активность:
                          </span>
                          <span className={styles.dateValue}>
                            {formatDate(user.lastActiveAt)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className={styles.userActions}>
                    {user.role === 'USER' && (
                      <Button
                        onClick={() => changeUserRole(user.id, 'ADMIN')}
                        variant={ButtonVariant.PRIMARY}
                        disabled={
                          actionLoading === user.id ||
                          changeUserRoleMutation.isPending
                        }
                        className={styles.actionBtn}
                      >
                        <Crown size={14} />
                        Сделать админом
                      </Button>
                    )}

                    {user.role === 'ADMIN' && (
                      <Button
                        onClick={() => changeUserRole(user.id, 'USER')}
                        variant={ButtonVariant.SECONDARY}
                        disabled={
                          actionLoading === user.id ||
                          changeUserRoleMutation.isPending
                        }
                        className={styles.actionBtn}
                      >
                        <UserX size={14} />
                        Убрать админа
                      </Button>
                    )}

                    {user.role !== 'GUEST' && (
                      <Button
                        onClick={() => deleteUser(user.id, user.email)}
                        variant={ButtonVariant.DANGER}
                        disabled={
                          actionLoading === user.id ||
                          deleteUserMutation.isPending
                        }
                        className={styles.actionBtn}
                      >
                        <Trash2 size={14} />
                        Удалить
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  );
};
