import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'

export const authOptions = {
  providers: [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: 'user:email repo',
        },
      },
    }),
  ],
  session: {
    strategy: 'jwt' as const,
  },
  callbacks: {
    async jwt({ token, account, profile }: any) {
      if (account && profile) {
        token.accessToken = account.access_token
        token.login = profile.login
        token.id = profile.id
      }
      return token
    },
    async session({ session, token }: any) {
      if (token.accessToken) {
        session.accessToken = token.accessToken
        session.user.login = token.login
        session.user.id = token.id
      }
      return session
    },
  },
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }

