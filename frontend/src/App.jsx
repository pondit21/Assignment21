import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

function App() {
  const [profile, setProfile] = useState(null)
  const [skills, setSkills] = useState([])
  const [projects, setProjects] = useState([])
  const [posts, setPosts] = useState([])
  const [experience, setExperience] = useState([])
  const [education, setEducation] = useState([])

  useEffect(() => {
    Promise.all([
      axios.get(`${API_URL}/profile/`),
      axios.get(`${API_URL}/skills/`),
      axios.get(`${API_URL}/projects/`),
      axios.get(`${API_URL}/posts/`),
      axios.get(`${API_URL}/experience/`),
      axios.get(`${API_URL}/education/`),
    ]).then(([profileRes, skillsRes, projectsRes, postsRes, experienceRes, educationRes]) => {
      setProfile(profileRes.data)
      setSkills(skillsRes.data)
      setProjects(projectsRes.data)
      setPosts(postsRes.data)
      setExperience(experienceRes.data)
      setEducation(educationRes.data)
    }).catch(() => {
      setProfile({ full_name: 'Rifat Hasan', headline: 'Full-stack developer', bio: 'I build modern web products with Django and React.' })
    })
  }, [])

  return (
    <Router>
      <div className="page-shell">
        <header className="site-header">
          <nav>
            <Link to="/">Home</Link>
            <Link to="/projects">Projects</Link>
            <Link to="/blog">Blog</Link>
            <Link to="/contact">Contact</Link>
          </nav>
        </header>
        <Routes>
          <Route path="/" element={<Home profile={profile} skills={skills} projects={projects} posts={posts} experience={experience} education={education} />} />
          <Route path="/projects" element={<Projects projects={projects} />} />
          <Route path="/projects/:slug" element={<ProjectDetail />} />
          <Route path="/blog" element={<Blog posts={posts} />} />
          <Route path="/blog/:slug" element={<PostDetail />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
      </div>
    </Router>
  )
}

function Home({ profile, skills, projects, posts, experience, education }) {
  return (
    <main className="home-page">
      <section className="hero-card">
        <div className="hero-text">
          <p className="eyebrow">FULL STACK DEVELOPER</p>
          <h1>{profile?.full_name || 'Rifat Hasan'}</h1>
          <p>{profile?.headline || 'I build reliable products with Django and React.'}</p>
          <div className="buttons">
            <Link className="btn primary" to="/projects">View Projects</Link>
            <a className="btn secondary" href="https://example.com" target="_blank" rel="noreferrer">Download Resume</a>
          </div>
        </div>
        <div className="photo-box">Photo</div>
      </section>

      <section className="section-row">
        <div className="card small-card">
          <h3>About</h3>
          <p>{profile?.bio || 'I build full-stack products and care about the details.'}</p>
        </div>
        <div className="card small-card">
          <h3>Skills</h3>
          <ul>{skills.slice(0, 6).map(skill => <li key={skill.id}>{skill.name}</li>)}</ul>
        </div>
      </section>

      <section className="card">
        <h3>Featured projects</h3>
        <div className="grid items-3">
          {projects.slice(0, 3).map(project => (
            <div key={project.id} className="project-box">
              <h4>{project.title}</h4>
              <p>{project.summary}</p>
              <Link to={`/projects/${project.slug}`}>Details →</Link>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h3>Experience</h3>
        {experience.map(item => (
          <div key={item.id} className="list-item">
            <strong>{item.role}</strong> — {item.company}
          </div>
        ))}
      </section>

      <section className="card">
        <h3>Education</h3>
        {education.map(item => (
          <div key={item.id} className="list-item">
            <strong>{item.degree}</strong> — {item.institution}
          </div>
        ))}
      </section>
    </main>
  )
}

function Projects({ projects }) {
  return (
    <main className="content-page">
      <h2>Projects</h2>
      <div className="grid items-3">
        {projects.map(project => (
          <div key={project.id} className="project-box large">
            <h3>{project.title}</h3>
            <p>{project.summary}</p>
            <Link to={`/projects/${project.slug}`}>Open project</Link>
          </div>
        ))}
      </div>
    </main>
  )
}

function ProjectDetail() {
  const { slug } = useParams()
  const [project, setProject] = useState(null)

  useEffect(() => {
    axios.get(`${API_URL}/projects/${slug}/`).then(({ data }) => setProject(data)).catch(() => {})
  }, [slug])

  if (!project) return <main className="content-page"><p>Loading project...</p></main>

  return (
    <main className="content-page">
      <h2>{project.title}</h2>
      <p>{project.summary}</p>
      <p>{project.description}</p>
    </main>
  )
}

function Blog({ posts }) {
  return (
    <main className="content-page">
      <h2>Blog</h2>
      <div className="blog-list">
        {posts.map(post => (
          <article key={post.id} className="card blog-item">
            <h3>{post.title}</h3>
            <p>{post.excerpt || post.content.slice(0, 120)}</p>
            <Link to={`/blog/${post.slug}`}>Read more</Link>
          </article>
        ))}
      </div>
    </main>
  )
}

function PostDetail() {
  const { slug } = useParams()
  const [post, setPost] = useState(null)

  useEffect(() => {
    axios.get(`${API_URL}/posts/${slug}/`).then(({ data }) => setPost(data)).catch(() => {})
  }, [slug])

  if (!post) return <main className="content-page"><p>Loading post...</p></main>

  return (
    <main className="content-page">
      <article className="card article">
        <h2>{post.title}</h2>
        <p>{post.excerpt}</p>
        <div dangerouslySetInnerHTML={{ __html: post.content }} />
      </article>
    </main>
  )
}

function Contact() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
  const [sent, setSent] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post(`${API_URL}/contact/`, form)
      setSent(true)
      setForm({ name: '', email: '', subject: '', message: '' })
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <main className="content-page">
      <h2>Contact</h2>
      <form className="contact-form" onSubmit={handleSubmit}>
        <input name="name" placeholder="Name" value={form.name} onChange={handleChange} required />
        <input name="email" placeholder="Email" type="email" value={form.email} onChange={handleChange} required />
        <input name="subject" placeholder="Subject" value={form.subject} onChange={handleChange} />
        <textarea name="message" placeholder="Your message" value={form.message} onChange={handleChange} required />
        <button className="btn primary" type="submit">Send message</button>
        {sent && <p>Thanks! Your message was sent.</p>}
      </form>
    </main>
  )
}

export default App
