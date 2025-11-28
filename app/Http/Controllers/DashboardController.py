"""
Dashboard Controller
"""
from app.Http.Controllers.Controller import Controller
from app.Http.Middleware.AuthMiddleware import require_auth, get_current_user
from app.Models.Post import Post
from app.Models.User import User


class DashboardController(Controller):
    """Handle dashboard operations"""
    
    @require_auth
    async def index(self, request):
        """Show dashboard home"""
        try:
            user = await get_current_user(request)
            print(f"DEBUG Dashboard: User = {user}")
            
            if not user:
                print("ERROR: User not found!")
                return self.redirect('/login')
            
            # Get user's posts (handle if table doesn't exist)
            try:
                posts = await Post.where('user_id', user.id).get()
                print(f"DEBUG Dashboard: Found {len(posts)} posts")
            except Exception as e:
                print(f"WARNING: Could not fetch posts: {e}")
                posts = []
            
            # Get stats
            total_posts = len(posts)
            published_posts = len([p for p in posts if hasattr(p, 'status') and p.status == 'published'])
            draft_posts = len([p for p in posts if hasattr(p, 'status') and p.status == 'draft'])
            
            return self.view('dashboard.index', request, {
                'user': user,
                'posts': posts[:5],  # Show last 5 posts
                'stats': {
                    'total_posts': total_posts,
                    'published': published_posts,
                    'drafts': draft_posts
                }
            })
        except Exception as e:
            print(f"ERROR Dashboard: {e}")
            import traceback
            traceback.print_exc()
            return self.view('dashboard.index', request, {
                'user': {'name': 'Guest', 'email': 'N/A'},
                'posts': [],
                'stats': {
                    'total_posts': 0,
                    'published': 0,
                    'drafts': 0
                },
                'error': str(e)
            })
