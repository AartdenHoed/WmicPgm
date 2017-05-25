using Microsoft.Owin;
using Owin;

[assembly: OwinStartupAttribute(typeof(ConfigMan.Startup))]
namespace ConfigMan
{
    public partial class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            ConfigureAuth(app);
        }
    }
}
